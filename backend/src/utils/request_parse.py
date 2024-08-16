#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import httpx

from asgiref.sync import sync_to_async
from fastapi import Request
from user_agents import parse
from XdbSearchIP.xdbSearcher import XdbSearcher

from src.common.log import log
from src.config.settings import settings
from src.config.path_conf import IP2REGION_XDB
from database.db_redis import redis_client


@sync_to_async
def get_request_ip(request: Request) -> str:
    """Get the request IP address."""
    real = request.headers.get('X-Real-IP')
    if real:
        ip = real
    else:
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            ip = forwarded.split(',')[0]
        else:
            ip = request.client.host # type: ignore
    # Ignore pytest
    if ip == 'testclient':
        ip = '127.0.0.1'
    return ip


async def get_location_online(ip: str, user_agent: str) -> dict | None:
    """
    Get IP address location online, accuracy may vary.

    :param ip: The IP address to lookup
    :param user_agent: User agent string
    :return: A dictionary with location information or None if failed
    """
    async with httpx.AsyncClient(timeout=3) as client:
        ip_api_url = f'http://ip-api.com/json/{ip}?lang=zh-CN'
        headers = {'User-Agent': user_agent}
        try:
            response = await client.get(ip_api_url, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            log.error(f'Failed to get IP location online, error: {e}')
            return None


@sync_to_async
def get_location_offline(ip: str) -> dict | None:
    """
    Get IP address location offline, accuracy may vary.

    :param ip: The IP address to lookup
    :return: A dictionary with location information or None if failed
    """
    try:
        cb = XdbSearcher.loadContentFromFile(dbfile=IP2REGION_XDB)
        searcher = XdbSearcher(contentBuff=cb)
        data = searcher.search(ip)
        searcher.close()
        data = data.split('|')
        return {
            'country': data[0] if data[0] != '0' else None,
            'regionName': data[2] if data[2] != '0' else None,
            'city': data[3] if data[3] != '0' else None,
        }
    except Exception as e:
        log.error(f'Failed to get IP location offline, error: {e}')
        return None


async def parse_ip_info(request: Request) -> tuple[str, str, str, str]:
    """
    Parse IP address information.

    :param request: The HTTP request
    :return: A tuple containing the IP, country, region, and city
    """
    country, region, city = None, None, None
    ip = await get_request_ip(request)
    location = await redis_client.get(f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}')
    if location:
        country, region, city = location.split(' ')
        return ip, country, region, city
    if settings.LOCATION_PARSE == 'online':
        location_info = await get_location_online(ip, request.headers.get('User-Agent')) # type: ignore
    elif settings.LOCATION_PARSE == 'offline':
        location_info = await get_location_offline(ip)
    else:
        location_info = None
    if location_info:
        country = location_info.get('country')
        region = location_info.get('regionName')
        city = location_info.get('city')
        await redis_client.set(
            f'{settings.IP_LOCATION_REDIS_PREFIX}:{ip}',
            f'{country} {region} {city}',
            ex=settings.IP_LOCATION_EXPIRE_SECONDS,
        )
    return ip, country, region, city # type: ignore


@sync_to_async
def parse_user_agent_info(request: Request) -> tuple[str, str, str, str]:
    """
    Parse user agent information.

    :param request: The HTTP request
    :return: A tuple containing the user agent, device, OS, and browser
    """
    user_agent = request.headers.get('User-Agent')
    _user_agent = parse(user_agent)
    device = _user_agent.get_device()
    os = _user_agent.get_os()
    browser = _user_agent.get_browser()
    return user_agent, device, os, browser # type: ignore
