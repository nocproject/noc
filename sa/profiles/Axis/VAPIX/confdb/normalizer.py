# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Axis.VAPIX config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.video.resolution import get_resolution


class VAPIXNormalizer(BaseNormalizer):
    @match("root", "Network", "HostName", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[3])

    @match("root", "Time", "TimeZone", ANY)
    def normalize_timezone(self, tokens):
        yield self.make_tz_offset(tz_name="", tz_offset=tokens[3])

    @match("root", "Time", "SynSource", "NTP")
    def normalize_timesource(self, tokens):
        yield self.make_clock_source(source="ntp")

    @match("root", "Time", "NTP", "Server", REST)
    def normalize_ntp_server(self, tokens):
        yield self.make_ntp_server_address(name="0", address=".".join(tokens[4:]))

    @match("root", "ImageSource", "I0", "Sensor", "WDR", ANY)
    @match("root", "ImageSource", "I0", "Sensor", "Wdr", ANY)
    def normalize_image_wdr(self, tokens):
        yield self.make_video_wide_dynamic_range_admin_status(
            name="default", admin_status=tokens[5] != "off"
        )

    @match("root", "ImageSource", "I0", "Sensor", "Backlight", ANY)
    def normalize_image_blc(self, tokens):
        yield self.make_video_black_light_compensation_admin_status(
            name="default", admin_status=tokens[5] == "on"
        )

    @match("root", "ImageSource", "I0", "Sensor", "Sharpness", ANY)
    def normalize_image_sharpness(self, tokens):
        yield self.make_video_sharpness(name="default", sharpness=tokens[5])

    @match("root", "ImageSource", "I0", "Sensor", "Brightness", ANY)
    def normalize_image_brightness(self, tokens):
        yield self.make_video_brightness(name="default", brightness=tokens[5])

    @match("root", "ImageSource", "I0", "Sensor", "WhiteBalance", ANY)
    def normalize_image_wb(self, tokens):
        yield self.make_video_white_balance_admin_status(
            name="default", admin_status=tokens[5] != "off"
        )
        if tokens[5] == "auto":
            yield self.make_video_white_balance_auto(name="default")

    @match("root", "Image", "I0", "Appearance", "Resolution", ANY)
    def normalize_resolution(self, tokens):
        for stream_name, resolution in [("h264", tokens[5]), ("mjpeg", tokens[5])]:
            if "x" in resolution:
                height, width = resolution.split("x")
            else:
                resolution = get_resolution(resolution.lower())
                height, width = resolution.height, resolution.width
            yield self.make_media_streams_video_admin_status(name=stream_name, admin_status=True)
            yield self.make_media_streams_video_resolution_height(name=stream_name, height=height)
            yield self.make_media_streams_video_resolution_width(name=stream_name, width=width)
            if stream_name == "mjpeg":
                yield self.make_media_streams_video_codec_mpeg4(name=stream_name)
                yield self.make_stream_rtsp_path(name=stream_name, path="/mjpg/video.mjpg")
            else:
                yield self.make_media_streams_video_codec_h264(name=stream_name)
                yield self.make_stream_rtsp_path(
                    name=stream_name, path="/axis-media/media.amp?videocodec=mpeg4"
                )

    @match("root", "Image", "I0", "RateControl", "Mode", ANY)
    def normalize_video_control_mode_h264(self, tokens):
        self.set_context("h264_use_vbr", tokens[5] == "vbr")
        # yield self.make_video_encoder_ratecontrol_mode(name="h264", mode=tokens[5].upper())
        yield

    @match("root", "Image", "I0", "RateControl", "TargetBitrate", ANY)
    @match("root", "Image", "I0", "RateControl", "MaxBitrate", ANY)
    def normalize_video_control_h264_2(self, tokens):
        if self.get_context("h264_use_vbr"):
            yield self.make_media_streams_video_rate_control_vbr_max_bitrate(
                name="h264", max_bitrate=tokens[5]
            )
        else:
            yield self.make_media_streams_video_rate_control_cbr_bitrate(
                name="h264", bitrate=tokens[5]
            )

    @match("root", "Image", "I0", "Appearance", "H264VideoKeyFrameInterval", ANY)
    def normalize_keyframe_h264(self, tokens):
        yield self.make_media_streams_video_codec_h264_profile_gov_length(
            name="h264", gov_length=tokens[5]
        )

    @match("root", "Audio", "DuplexMode", ANY)
    def normalize_stream_audio_enable(self, tokens):
        yield self.make_media_streams_audio_admin_status(
            name="h264", admin_status=tokens[3] != "disable"
        )

    @match("root", "Image", "I0", "Text", "String", REST)
    def normalize_overlay_text_text(self, tokens):
        yield self.make_media_streams_overlay_status(overlay_name="channel_name", admin_status=True)
        yield self.make_media_streams_overlay_text(
            overlay_name="channel_name", text=" ".join(tokens[5:])
        )

    @match("user", ANY)
    def normalize_username(self, tokens):
        tk = tokens[1].split(":")
        if tk[0] != "Username":
            yield self.make_user_class(username=tk[0], class_name=":".join(tk[1:]))
