import json
from json import JSONDecodeError

import pytest

from teleinforeader.model.tele_info_data import TeleInfoFrame


def create_correct_json_data() -> dict:
    json_dict = {
        'timestamp': '1970-01-02_16:01:59.999',
        'frame': {
            'ADCO': 'ABCDEF123456',
            'OPTARIF': 'EFGH',
            'ISOUSC': 10,
            'BASE': 555666,
            'PTEC': 'IJKL',
            'IINST': 20,
            'IMAX': 30,
            'PAPP': 40,
            'HHPHC': 'Z',
            'MOTDETAT': 'XYZ987'
        }
    }
    return json_dict


def test_tele_info_data_with_empty_constructor():
    data = TeleInfoFrame()

    assert data.timestamp == ''
    assert data.timestamp_db == ''
    assert data.meter_identifier == ''
    assert data.subscription_type == ''
    assert data.subscription_power_in_a == 0
    assert data.total_base_index_in_wh == 0
    assert data.current_pricing_period == ''
    assert data.instantaneous_intensity_in_a == 0
    assert data.intensity_max_in_a == 0
    assert data.power_consumption_in_va == 0
    assert data.peak_off_peak_schedule == ''
    assert data.meter_state_code == ''


def test_tele_info_data_with_correct_json():
    correct_json_str = json.dumps(create_correct_json_data())

    data = TeleInfoFrame(correct_json_str)

    assert data.timestamp == '1970-01-02_16:01:59.999'
    assert data.timestamp_db == '1970-01-02_16:01:59'
    assert data.meter_identifier == 'ABCDEF123456'
    assert data.subscription_type == 'EFGH'
    assert data.subscription_power_in_a == 10
    assert data.total_base_index_in_wh == 555666
    assert data.current_pricing_period == 'IJKL'
    assert data.instantaneous_intensity_in_a == 20
    assert data.intensity_max_in_a == 30
    assert data.power_consumption_in_va == 40
    assert data.peak_off_peak_schedule == 'Z'
    assert data.meter_state_code == 'XYZ987'


def test_tele_info_data_with_invalid_json_format():
    json_str_with_curly_brace_removed = '{"timestamp": "foo"'

    with pytest.raises(JSONDecodeError) as e:
        TeleInfoFrame(json_str_with_curly_brace_removed)

    assert str(e.value) == "Expecting ',' delimiter: line 1 column 20 (char 19)"


def test_tele_info_data_with_invalid_json_data_type_int_str():
    json_str_with_invalid_adco_data_type = create_correct_json_data()
    json_str_with_invalid_adco_data_type['frame']['ADCO'] = 99
    invalid_json_str = json.dumps(json_str_with_invalid_adco_data_type)

    with pytest.raises(TypeError) as e:
        TeleInfoFrame(invalid_json_str)

    assert str(e.value) == 'meter_identifier expects str type'


def test_tele_info_data_with_invalid_json_data_type_str_int():
    json_str_with_invalid_instantaneous_intensity_data_type = create_correct_json_data()
    json_str_with_invalid_instantaneous_intensity_data_type['frame']['IINST'] = 'foo'
    invalid_json_str = json.dumps(json_str_with_invalid_instantaneous_intensity_data_type)

    with pytest.raises(ValueError) as e:
        TeleInfoFrame(invalid_json_str)

    assert str(e.value) == "invalid literal for int() with base 10: 'foo'"


def test_tele_info_data_to_string():
    correct_json_str = json.dumps(create_correct_json_data())

    assert str(TeleInfoFrame(correct_json_str)) == \
           '{\n' \
           '\tTimestamp: 1970-01-02_16:01:59.999\n' \
           '\tADCO: ABCDEF123456\t# Meter identifier\n' \
           '\tOPTARIF: EFGH\t\t# Subscription type\n' \
           '\tISOUSC: 10 A\t\t# Subscription power\n' \
           '\tBASE: 555666 W.h\t# Total base index\n' \
           '\tPTEC: IJKL\t\t\t# Current pricing method\n' \
           '\tIINST: 20 A\t\t\t# Current intensity\n' \
           '\tIMAX: 30 A\t\t\t# Max intensity\n' \
           '\tPAPP: 40 V.A\t\t# Power consumption\n' \
           '\tHHPHC: Z\t\t\t# Peak/Off-peak time schedule\n' \
           '\tError Code: XYZ987\n' \
           '}'
