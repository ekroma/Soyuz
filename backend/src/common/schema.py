#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel, ConfigDict, EmailStr, validate_email
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import TypeVar, Generic

T = TypeVar("T")


CUSTOM_VALIDATION_ERROR_MESSAGES = {
    'arguments_type': 'Incorrect argument type',
    'assertion_error': 'Assertion error',
    'bool_parsing': 'Boolean value parsing error',
    'bool_type': 'Incorrect boolean value type',
    'bytes_too_long': 'Bytes length too long',
    'bytes_too_short': 'Bytes length too short',
    'bytes_type': 'Incorrect bytes type',
    'callable_type': 'Incorrect callable type',
    'dataclass_exact_type': 'Incorrect dataclass instance type',
    'dataclass_type': 'Incorrect dataclass type',
    'date_from_datetime_inexact': 'Non-zero date component',
    'date_from_datetime_parsing': 'Date parsing error',
    'date_future': 'Date is not in the future',
    'date_parsing': 'Date validation error',
    'date_past': 'Date is not in the past',
    'date_type': 'Incorrect date type',
    'datetime_future': 'Datetime is not in the future',
    'datetime_object_invalid': 'Invalid datetime object',
    'datetime_parsing': 'Datetime parsing error',
    'datetime_past': 'Datetime is not in the past',
    'datetime_type': 'Incorrect datetime type',
    'decimal_max_digits': 'Too many decimal places',
    'decimal_max_places': 'Incorrect number of decimal places',
    'decimal_parsing': 'Decimal parsing error',
    'decimal_type': 'Incorrect decimal type',
    'decimal_whole_digits': 'Incorrect number of decimal digits',
    'dict_type': 'Incorrect dictionary type',
    'enum': 'Incorrect enum member, allowed {expected}',
    'extra_forbidden': 'Extra fields are not allowed',
    'finite_number': 'Finite number expected',
    'float_parsing': 'Float parsing error',
    'float_type': 'Incorrect float type',
    'frozen_field': 'Frozen field modification error',
    'frozen_instance': 'Modification of frozen instance is not allowed',
    'frozen_set_type': 'Modification of frozen set is not allowed',
    'get_attribute_error': 'Error in getting attribute',
    'greater_than': 'Value is too large',
    'greater_than_equal': 'Value is too large or equal',
    'int_from_float': 'Incorrect integer type from float',
    'int_parsing': 'Integer parsing error',
    'int_parsing_size': 'Integer parsing size error',
    'int_type': 'Incorrect integer type',
    'invalid_key': 'Invalid key value',
    'is_instance_of': 'Incorrect instance type',
    'is_subclass_of': 'Incorrect subclass type',
    'iterable_type': 'Incorrect iterable type',
    'iteration_error': 'Iteration error',
    'json_invalid': 'Invalid JSON string',
    'json_type': 'Incorrect JSON type',
    'less_than': 'Value is too small',
    'less_than_equal': 'Value is too small or equal',
    'list_type': 'Incorrect list type',
    'literal_error': 'Incorrect literal value',
    'mapping_type': 'Incorrect mapping type',
    'missing': 'Missing required field',
    'missing_argument': 'Missing argument',
    'missing_keyword_only_argument': 'Missing keyword-only argument',
    'missing_positional_only_argument': 'Missing positional-only argument',
    'model_attributes_type': 'Incorrect model attribute type',
    'model_type': 'Incorrect model instance type',
    'multiple_argument_values': 'Too many argument values',
    'multiple_of': 'Value is not a multiple of required value',
    'no_such_attribute': 'Assigning invalid attribute value',
    'none_required': 'Value must be None',
    'recursion_loop': 'Recursion loop detected',
    'set_type': 'Incorrect set type',
    'string_pattern_mismatch': 'String pattern mismatch',
    'string_sub_type': 'Incorrect string subtype',
    'string_too_long': 'String length too long',
    'string_too_short': 'String length too short',
    'string_type': 'Incorrect string type',
    'string_unicode': 'String is not Unicode',
    'time_delta_parsing': 'Timedelta parsing error',
    'time_delta_type': 'Incorrect timedelta type',
    'time_parsing': 'Time parsing error',
    'time_type': 'Incorrect time type',
    'timezone_aware': 'Missing timezone information',
    'timezone_naive': 'Timezone information not allowed',
    'too_long': 'Value too long',
    'too_short': 'Value too short',
    'tuple_type': 'Incorrect tuple type',
    'unexpected_keyword_argument': 'Unexpected keyword argument',
    'unexpected_positional_argument': 'Unexpected positional argument',
    'union_tag_invalid': 'Invalid union tag',
    'union_tag_not_found': 'Union tag not found',
    'url_parsing': 'URL parsing error',
    'url_scheme': 'Incorrect URL scheme',
    'url_syntax_violation': 'URL syntax violation',
    'url_too_long': 'URL too long',
    'url_type': 'Incorrect URL type',
    'uuid_parsing': 'UUID parsing error',
    'uuid_type': 'Incorrect UUID type',
    'uuid_version': 'Incorrect UUID version',
    'value_error': 'Value error',
}

CUSTOM_USAGE_ERROR_MESSAGES = {
    'class-not-fully-defined': 'Class attribute type not fully defined',
    'custom-json-schema': '__modify_schema__ method deprecated in V2',
    'decorator-missing-field': 'Invalid field validator defined',
    'discriminator-no-field': 'Discriminator field not fully defined',
    'discriminator-alias-type': 'Discriminator field must be a string',
    'discriminator-needs-literal': 'Discriminator field needs a literal value',
    'discriminator-alias': 'Discriminator field alias mismatch',
    'discriminator-validator': 'Discriminator field cannot have a validator',
    'model-field-overridden': 'Cannot override a field without a type',
    'model-field-missing-annotation': 'Missing field type annotation',
    'config-both': 'Duplicate configuration options defined',
    'removed-kwargs': 'Calling a removed keyword configuration parameter',
    'invalid-for-json-schema': 'Invalid JSON type',
    'base-model-instantiated': 'Cannot instantiate base model',
    'undefined-annotation': 'Missing type annotation',
    'schema-for-unknown-type': 'Unknown type annotation',
    'create-model-field-definitions': 'Field definition error',
    'create-model-config-base': 'Configuration definition error',
    'validator-no-fields': 'Validator must specify fields',
    'validator-invalid-fields': 'Validator field definition error',
    'validator-instance-method': 'Validator must be a class method',
    'model-serializer-instance-method': 'Serializer must be an instance method',
    'validator-v1-signature': 'V1 validator signature is deprecated',
    'validator-signature': 'Validator signature error',
    'field-serializer-signature': 'Field serializer signature not recognized',
    'model-serializer-signature': 'Model serializer signature not recognized',
    'multiple-field-serializers': 'Duplicate field serializers defined',
    'invalid_annotated_type': 'Invalid annotated type',
    'type-adapter-config-unused': 'Type adapter configuration error',
    'root-model-extra': 'Root model cannot have extra fields',
}

class CustomPhoneNumber(PhoneNumber):
    # default_region_code = 'KG'
    pass

class CustomEmailStr(EmailStr):
    @classmethod
    def _validate(cls, __input_value: str) -> str:
        return None if __input_value == '' else validate_email(__input_value)[1]  # type: ignore

class SchemaBase(BaseModel):

    class Config:
        use_enum_values = True

class TranslateSchema(BaseModel, Generic[T]):
    translates:dict[str,T]
