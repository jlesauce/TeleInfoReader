import json


class TeleInfoFrame:

    def __init__(self, tele_info_frame_json=None):
        if tele_info_frame_json is None:
            self.timestamp = ''
            self.timestamp_db = ''
            self.meter_identifier = ''
            self.subscription_type = ''
            self.subscription_power_in_a = 0
            self.total_base_index_in_wh = 0
            self.current_pricing_period = ''
            self.instantaneous_intensity_in_a = 0
            self.intensity_max_in_a = 0
            self.power_consumption_in_va = 0
            self.peak_off_peak_schedule = ''
            self.meter_state_code = ''
        else:
            self._update_data(tele_info_frame_json)

    def _update_data(self, tele_info_frame_json: str):
        json_data = json.loads(tele_info_frame_json)

        self.timestamp = json_data['timestamp']
        self.timestamp_db, _, _ = self.timestamp.partition('.')
        tele_info_data_dict = json_data['frame']

        self.meter_identifier = tele_info_data_dict['ADCO']
        self.subscription_type = tele_info_data_dict['OPTARIF']
        self.subscription_power_in_a = int(tele_info_data_dict['ISOUSC'])
        self.total_base_index_in_wh = int(tele_info_data_dict['BASE'])
        self.current_pricing_period = tele_info_data_dict['PTEC']
        self.instantaneous_intensity_in_a = int(tele_info_data_dict['IINST'])
        self.intensity_max_in_a = int(tele_info_data_dict['IMAX'])
        self.power_consumption_in_va = int(tele_info_data_dict['PAPP'])
        self.peak_off_peak_schedule = tele_info_data_dict['HHPHC']
        self.meter_state_code = tele_info_data_dict['MOTDETAT']

    def __str__(self):
        return '{\n' \
               f'\tTimestamp: {self.timestamp}\n' \
               f'\tADCO: {self.meter_identifier}\t# Meter identifier\n' \
               f'\tOPTARIF: {self.subscription_type}\t\t# Subscription type\n' \
               f'\tISOUSC: {self.subscription_power_in_a} A\t\t# Subscription power\n' \
               f'\tBASE: {self.total_base_index_in_wh} W.h\t# Total base index\n' \
               f'\tPTEC: {self.current_pricing_period}\t\t\t# Current pricing method\n' \
               f'\tIINST: {self.instantaneous_intensity_in_a} A\t\t\t# Current intensity\n' \
               f'\tIMAX: {self.intensity_max_in_a} A\t\t\t# Max intensity\n' \
               f'\tPAPP: {self.power_consumption_in_va} V.A\t\t# Power consumption\n' \
               f'\tHHPHC: {self.peak_off_peak_schedule}\t\t\t# Peak/Off-peak time schedule\n' \
               f'\tError Code: {self.meter_state_code}\n' \
               '}'
