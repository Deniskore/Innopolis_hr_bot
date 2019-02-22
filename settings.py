import json


class Settings:
    def __init__(self):
        with open('settings.json', 'r', encoding='utf-8') as settings_file:
            self.settings = json.load(settings_file)
        self.week_days = self.__get_week_days()
        self.admins = self.__get_admins()
        self.bot_token = self.__get_bot_token()
        self.private_channel_id = self.__get_private_channel_id()
        self.max_requests = self.__get_max_requests()
        self.start_of_day = self.__get_start_time()
        self.end_of_day = self.__get_end_time()
        self.image_path = self.__get_image_path()
        self.reply_first = self.__get_reply_first()
        self.reply_first_regex = self.__get_reply_first_regex()
        self.reply_cancel = self.__get_reply_cancel()
        self.reply_cancel_regex = self.__get_reply_cancel_regex()
        self.msg_link_to_cv = self.__get_msg_link_to_cv()
        self.msg_choose_menu_item = self.__get_msg_choose_menu_item()
        self.msg_send_cv_link = self.__get_msg_send_cv_link()
        self.msg_cv_received = self.__get_msg_cv_received()
        self.msg_incorrect_url = self.__get_msg_incorrect_url()
        self.msg_already_reserved = self.__get_msg_already_reserved()
        self.msg_interview_canceled = self.__get_msg_canceled()
        self.msg_choose_date = self.__get_msg_choose_date()
        self.msg_choose_time = self.__get_msg_choose_time()
        self.msg_chose_date = self.__get_msg_chose_date()
        self.msg_chose_time = self.__get_msg_chose_time()
        self.msg_canceled_interview = self.__get_msg_canceled_interview()
        self.msg_noreserved_interview = self.__get_msg_noreserved_interview()
        self.msg_callback_date_picked = self.__get_msg_callback_date_picked()
        self.msg_callback_time_picked = self.__get_msg_callback_time_picked()
        self.msg_innopolis_info = self.__get_msg_innopolis_info()
        self.msg_someone_reserved = self.__get_msg_someone_reserved()
        self.msg_start = self.__get_msg_start()
        self.msg_interview_limit_exceeded = self.__get_msg_limit_exceeded()
        self.msg_minutes_rem = self.__get_msg_minutes_rem()
        self.msg_no_coming_interviews = self.__get_msg_no_coming_interviews()
        self.msg_list_interviews = self.__get_msg_list_interviews()

    def __get_week_days(self):
        return self.settings['weekDays']

    def __get_admins(self):
        return self.settings['admins']

    def __get_bot_token(self):
        return self.settings['botToken']

    def __get_private_channel_id(self):
        return int(self.settings['privateChannelId'])

    def __get_max_requests(self):
        return int(self.settings['maxInterviewRequestsPerDay'])

    def __get_start_time(self):
        return int(self.settings['startOfDay'])

    def __get_end_time(self):
        return int(self.settings['endOfDay'])

    def __get_image_path(self):
        return self.settings['imagesPath']

    def __get_reply_first(self):
        return self.settings['replyKeyboardFirst']

    def __get_reply_first_regex(self):
        return self.settings['replyKeyboardFirstRegex']

    def __get_reply_cancel(self):
        return self.settings['replyKeyboardCancel']

    def __get_reply_cancel_regex(self):
        return self.settings['replyKeyboardCancelRegex']

    def __get_msg_link_to_cv(self):
        return self.settings['msgLinkToCV']

    def __get_msg_choose_menu_item(self):
        return self.settings['msgChooseMenuItem']

    def __get_msg_send_cv_link(self):
        return self.settings['msgSendCVLink']

    def __get_msg_cv_received(self):
        return self.settings['msgCVLinkReceived']

    def __get_msg_incorrect_url(self):
        return self.settings['msgIncorrectUrl']

    def __get_msg_already_reserved(self):
        return self.settings['msgAlreadyReserved']

    def __get_msg_canceled(self):
        return self.settings['msgInterviewCanceled']

    def __get_msg_choose_date(self):
        return self.settings['msgPlsChooseDate']

    def __get_msg_choose_time(self):
        return self.settings['msgPlsChooseTime']

    def __get_msg_chose_date(self):
        return self.settings['msgChoseDate']

    def __get_msg_chose_time(self):
        return self.settings['msgChoseTime']

    def __get_msg_canceled_interview(self):
        return self.settings['msgCanceledInterview']

    def __get_msg_noreserved_interview(self):
        return self.settings['msgNoReservedInterview']

    def __get_msg_innopolis_info(self):
        return self.settings['msgInnopolisInfo']

    def __get_msg_someone_reserved(self):
        return self.settings['msgSomeoneReservedInterview']

    def __get_msg_start(self):
        return self.settings['msgStart']

    def __get_msg_callback_date_picked(self):
        return self.settings['msgCallbackDatePicked']

    def __get_msg_callback_time_picked(self):
        return self.settings['msgCallbackTimePicked']

    def __get_msg_limit_exceeded(self):
        return self.settings['msgLimitExceeded']

    def __get_msg_minutes_rem(self):
        return self.settings['msgMinutesRem']

    def __get_msg_no_coming_interviews(self):
        return self.settings['msgNoComingInterviews']

    def __get_msg_list_interviews(self):
        return self.settings['msgListOfInterviews']


ss = Settings()
