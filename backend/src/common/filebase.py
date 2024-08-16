import os
from fastapi import UploadFile
from pathlib import Path

from src.config.settings import settings

class FileBase:

    @staticmethod
    async def save_upload_file(upload_file: UploadFile, destination_path:str="") -> str:
        file_name:str|None = upload_file.filename
        if not file_name:
            raise  ValueError("No filename provided")
        domain_path = "default"
        save_file_path:str = os.path.join(settings.MEDIA_ROOT,domain_path,destination_path,file_name)
        os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
        with open(save_file_path, "wb") as buffer:
            data = await upload_file.read()
            buffer.write(data)
        await upload_file.close()
        file_path = os.path.join(settings.BASE_URL,settings.MEDIA_DIR,domain_path,destination_path,file_name)
        return file_path
    
    @staticmethod
    async def delete_file(file: str):
        file_path = Path(file)
        if file_path.exists():
            os.remove(file_path)
            return {"message": f"File {file_path} deleted"}
        else:
            return {"message": f"File {file_path} not found"}