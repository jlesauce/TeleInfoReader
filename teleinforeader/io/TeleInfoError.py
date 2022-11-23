class TeleInfoError(Exception):

    def __init__(self, error: Exception, tele_info_frame: str):
        self.error = error
        self.tele_info_frame = tele_info_frame
        super().__init__(self.error)
