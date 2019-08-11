# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Hikvision.DSKV8 config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST


class HikvisionNormalizer(BaseNormalizer):
    # config format: table.<entityname>[entityToken].

    @match("DeviceInfo", "deviceName", REST)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(hostname=" ".join(tokens[2:]))

    @match("Time", "timeZone", ANY)
    def normalize_timezone(self, tokens):
        name, offset = tokens[2].split("-")
        yield self.make_tz_offset(tz_name=name, tz_offset=offset)

    @match("Time", "timeMode", "NTP")
    def normalize_timesource(self, tokens):
        yield self.make_clock_source(source="ntp")

    @match("Time", "NTPServer", ANY, ANY)
    def normalize_ntp_server(self, tokens):
        yield self.make_ntp_server_address(name=tokens[2], address=tokens[3])

    @match("Users", "user", ANY, "userLevel", ANY)
    def normalize_username_access_level(self, tokens):
        yield self.make_user_class(username=tokens[2], class_name="level-%s" % tokens[4].lower())

    @match("Users", "user", ANY, "id", ANY)
    def normalize_username_uid(self, tokens):
        yield self.make_user_uid(username=tokens[2], uid=tokens[4])

    @match("Color", "brightnessLevel", ANY)
    def normalize_image_profile_brightness(self, tokens):
        yield self.make_video_brightness(name="1", brightness=tokens[2])

    @match("Color", "contrastLevel", ANY)
    def normalize_image_profile_contrast(self, tokens):
        yield self.make_video_contrast(name="1", contrast=tokens[2])

    @match("Color", "saturationLevel", ANY)
    def normalize_image_profile_saturation(self, tokens):
        yield self.make_video_saturation(name="1", saturation=tokens[2])

    @match("WDR", "mode", ANY)
    def normalize_image_wdr(self, tokens):
        yield self.make_video_wide_dynamic_range_admin_status(
            name="1", admin_status={"open": True, "close": False, "auto": True}[tokens[2]]
        )

    @match("WDR", "WDRLevel", ANY)
    def normalize_image_wdr_level(self, tokens):
        yield self.make_video_wide_dynamic_range_level(name="1", level=tokens[2])

    @match("BLC", "enabled", ANY)
    def normalize_image_blc(self, tokens):
        yield self.make_video_black_light_compensation_admin_status(
            name="1", admin_status=tokens[2] == "true"
        )

    @match("StreamingChannel", ANY, "enabled", ANY)
    def normalize_stream_enable(self, tokens):
        yield self.make_stream_rtsp_path(name=tokens[1], path="/Streaming/Channels/%s" % tokens[1])
        yield self.make_media_streams_video_admin_status(
            name=tokens[1], admin_status=tokens[3] == "true"
        )

    @match("StreamingChannel", ANY, "Video", "videoResolutionHeight", ANY)
    def normalize_resolution_height(self, tokens):
        yield self.make_media_streams_video_resolution_height(name=tokens[1], height=tokens[4])

    @match("StreamingChannel", ANY, "Video", "videoResolutionWidth", ANY)
    def normalize_resolution_width(self, tokens):
        yield self.make_media_streams_video_resolution_width(name=tokens[1], width=tokens[4])

    @match("StreamingChannel", ANY, "Video", "vbrUpperCap", ANY)
    def normalize_vbr_bitrate(self, tokens):
        yield self.make_media_streams_video_rate_control_vbr_max_bitrate(
            name=tokens[1], max_bitrate=tokens[4]
        )

    @match("StreamingChannel", ANY, "Video", "constantBitRate", ANY)
    def normalize_cbr_bitrate(self, tokens):
        yield self.make_media_streams_video_rate_control_cbr_bitrate(
            name=tokens[1], bitrate=tokens[4]
        )

    @match("StreamingChannel", ANY, "Video", "videoCodecType", "H.264")
    def normalize_encoder_compression(self, tokens):
        yield self.make_media_streams_video_codec_h264(name=tokens[1])

    @match("StreamingChannel", ANY, "Video", "GovLength", ANY)
    def normalize_h264_keyframe_(self, tokens):
        yield self.make_media_streams_video_codec_h264_profile_gov_length(
            name=tokens[1], gov_length=tokens[4]
        )

    @match("StreamingChannel", ANY, "Video", "maxFrameRate", ANY)
    def normalize_h264_framerate_(self, tokens):
        yield self.make_media_streams_video_rate_control_max_framerate(
            name=tokens[1], max_framerate=int(tokens[4]) / 100
        )

    @match("StreamingChannel", ANY, "Video", "H264Profile", ANY)
    def normalize_h264_profile(self, tokens):
        yield self.make_media_streams_video_codec_h264_profile_name(
            name=tokens[1], profile=tokens[4]
        )

    @match("StreamingChannel", ANY, "Audio", "enabled", ANY)
    def normalize_stream_audio_enable(self, tokens):
        yield self.make_media_streams_audio_admin_status(
            name=tokens[1], admin_status=tokens[4] == "true"
        )

    @match("StreamingChannel", ANY, "Audio", "audioCompressionType", ANY)
    def normalize_stream_audio_encoder(self, tokens):
        codec = tokens[4].lower().replace(".", "")
        yield self.make_media_streams_audio_codec(name=tokens[1], codec=codec[:5])

    @match("Overlay", "channelNameOverlay", "enabled", ANY)
    def normalize_overlay_channel_name_enable(self, tokens):
        yield self.make_media_streams_overlay_status(
            admin_status=tokens[3] == "true", overlay_name="channel_name"
        )

    @match("Overlay", "channelNameOverlay", "channelName", ANY)
    def normalize_overlay_channel_name_text(self, tokens):
        yield self.make_media_streams_overlay_text(overlay_name="channel_name", text=tokens[3])

    @match("Overlay", "DateTimeOverlay", "enabled", ANY)
    def normalize_overlay_datetime_enable(self, tokens):
        yield self.make_media_streams_overlay_status(
            admin_status=tokens[3] == "true", overlay_name="datetime"
        )

    @match("Overlay", "TextOverlay", "TextOverlay", ANY, ANY)
    def normalize_overlay_text_text(self, tokens):
        yield self.make_media_streams_overlay_text(
            overlay_name="custom_%s" % tokens[3], text=tokens[4]
        )
