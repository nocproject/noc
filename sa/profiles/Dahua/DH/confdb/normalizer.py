# ----------------------------------------------------------------------
# Dahua.DH config normalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST, deferable
from noc.core.validators import is_ipv4


class DHNormalizer(BaseNormalizer):
    # config format: table.<entityname>[entityToken].

    @staticmethod
    def get_channel_name(fmt, subtype):
        # MainFormat[0] - MainStream: channel=1, Subtype=0
        # ExtraFormat[0] - ExtraStream 1: channel=1, Subtype=1
        # ExtraFormat[1] - ExtraStream 2: channel=1, Subtype=2
        # ExtraFormat[2] - ExtraStream 3: channel=1, Subtype=3
        # ExtraStreamCount is GetMaxStreamCounts MaxExtraStream is {1,2,3}
        return {
            ("MainFormat", "0"): "main",
            ("ExtraFormat", "0"): "extra_1",
            ("ExtraFormat", "1"): "extra_2",
            ("ExtraFormat", "2"): "extra_3",
        }.get((fmt, subtype))

    @match("table", "Network", "Hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[3])

    @match("table", "NTP", "TimeZone", ANY)
    def normalize_timezone(self, tokens):
        yield self.make_tz_offset(tz_name="", tz_offset=tokens[3])

    @match("table", "NTP", "Enable", ANY)
    def normalize_timesource(self, tokens):
        if tokens[3] == "true":
            yield self.make_clock_source(source="ntp")

    @match("table", "NTP", "Address", REST)
    def normalize_ntp_server(self, tokens):
        if is_ipv4(".".join(tokens[3:])):
            yield self.make_ntp_server_address(name="0", address=".".join(tokens[3:]))

    @match("users", ANY, "Name", ANY)
    def normalize_user_name(self, tokens):
        yield self.defer("user.%s" % tokens[1], username=tokens[3])

    @match("users", ANY, "Memo", REST)
    def normalize_user_full_name(self, tokens):
        yield self.defer(
            "user.%s" % tokens[1],
            self.make_user_full_name,
            username=deferable("username"),
            full_name=" ".join(tokens[3:]),
        )

    @match("users", ANY, "Id", ANY)
    def normalize_user_uid(self, tokens):
        yield self.defer(
            "user.%s" % tokens[1], self.make_user_uid, username=deferable("username"), uid=tokens[3]
        )

    @match("table", "VideoColor", ANY, "0", "Brightness", ANY)
    def normalize_image_profile_brightness(self, tokens):
        yield self.make_video_brightness(name="0", brightness=tokens[5])
        # yield self.make_image_brightness(profile_name="MediaProfile002", brightness=tokens[5])

    @match("table", "VideoColor", ANY, "0", "Contrast", ANY)
    def normalize_image_profile_contrast(self, tokens):
        yield self.make_video_contrast(name="0", contrast=tokens[5])
        # yield self.make_image_contrast(profile_name="MediaProfile002", contrast=tokens[5])

    @match("table", "VideoColor", ANY, "0", "Saturation", ANY)
    def normalize_image_profile_saturation(self, tokens):
        yield self.make_video_saturation(name="0", saturation=tokens[5])
        # yield self.make_image_saturation(profile_name="MediaProfile002", saturation=tokens[5])

    @match("table", "VideoInOptions", "0", "WideDynamicRangeMode", ANY)
    def normalize_image_wdr(self, tokens):
        yield self.make_video_wide_dynamic_range_admin_status(
            name="0", admin_status=tokens[4] != "0"
        )

    @match("table", "VideoInOptions", "0", "Backlight", ANY)
    def normalize_image_blc(self, tokens):
        yield self.make_video_black_light_compensation_admin_status(
            name="0", admin_status=tokens[4] != "0"
        )

    @match("table", "VideoInOptions", "0", "WhiteBalance", ANY)
    def normalize_image_wb(self, tokens):
        yield self.make_video_white_balance_admin_status(
            name="0", admin_status=tokens[4].lower() != "off"
        )
        if tokens[4].lower() == "auto":
            yield self.make_video_white_balance_auto(name="0")

    @match("table", "Encode", "0", ANY, ANY, "VideoEnable", ANY)
    def normalize_extra_stream_enable(self, tokens):
        channel, subtype = "1", tokens[4]
        name = self.get_channel_name(tokens[3], subtype)
        if tokens[3] == "ExtraFormat":
            subtype = int(subtype) + 1
        if name:
            yield self.make_media_streams_video_admin_status(
                name=name, admin_status=tokens[6] != "false"
            )
            yield self.make_stream_rtsp_path(
                name=name,
                path="/cgi-bin/realmonitor.cgi?action=getStream&channel=%s&subtype=%s"
                % (channel, subtype),
            )

    @match("table", "Encode", "0", ANY, ANY, "Video", "resolution", ANY)
    def normalize_resolution(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        width, height = tokens[7].split("x")
        if name:
            yield self.make_media_streams_video_resolution_height(name=name, height=height)
            yield self.make_media_streams_video_resolution_width(name=name, width=width)

    @match("table", "Encode", "0", ANY, ANY, "Video", "BitRateControl", ANY)
    def normalize_video_control_mode(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        bitrate = self.get_context("%s_bitrate" % name)
        if name and tokens[7].upper() == "VBR":
            yield self.make_media_streams_video_rate_control_vbr_max_bitrate(
                name=name, max_bitrate=bitrate
            )
        elif name:
            # CBR
            yield self.make_media_streams_video_rate_control_cbr_bitrate(name=name, bitrate=bitrate)
        else:
            yield

    @match("table", "Encode", "0", ANY, ANY, "Video", "BitRate", ANY)
    def normalize_bitrate(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        if name:
            self.set_context("%s_bitrate" % name, tokens[7])
        yield

    @match("table", "Encode", "0", ANY, ANY, "Video", "FPS", ANY)
    def normalize_h264_framerate_(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        if name:
            yield self.make_media_streams_video_rate_control_max_framerate(
                name=name, max_framerate=tokens[7]
            )

    @match("table", "Encode", "0", ANY, ANY, "Video", "Compression", REST)
    def normalize_encoder_compression(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        codec = "".join(tokens[7:])
        if name and codec == "MJPG":
            yield self.make_media_streams_video_codec_mpeg4(name=name)
        elif name:
            yield self.make_media_streams_video_codec_h264(name=name)
        else:
            yield

    @match("table", "Encode", "0", ANY, ANY, "Video", "GOP", ANY)
    def normalize_h264_keyframe(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        if name:
            yield self.make_media_streams_video_codec_h264_profile_gov_length(
                name=name, gov_length=tokens[7]
            )

    @match("table", "Encode", "0", ANY, ANY, "Video", "Profile", ANY)
    def normalize_h264_profile(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        if name:
            yield self.make_media_streams_video_codec_h264_profile_name(
                name=name, profile=tokens[7]
            )

    @match("table", "Encode", "0", ANY, ANY, "AudioEnable", ANY)
    def normalize_stream_audio_enable(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        if name:
            yield self.make_media_streams_audio_admin_status(
                name=name, admin_status=tokens[6] == "true"
            )

    @match("table", "Encode", "0", ANY, ANY, "Audio", "Compression", REST)
    def normalize_stream_audio_encoder(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        codec = "".join(tokens[7:])
        if name:
            yield self.make_media_streams_audio_codec(name=name, codec=codec.lower())

    @match("table", "Encode", "0", ANY, ANY, "Audio", "Bitrate", ANY)
    def normalize_stream_audio_bitrate(self, tokens):
        name = self.get_channel_name(tokens[3], tokens[4])
        if name:
            yield self.make_media_streams_audio_bitrate(name=name, bitrate=tokens[7])

    @match("table", "VideoWidget", "0", "ChannelTitle", "EncodeBlend", ANY)
    def normalize_overlay_channel_name_enable(self, tokens):
        yield self.make_media_streams_overlay_status(
            admin_status=tokens[5] == "true", overlay_name="ChannelTitle"
        )

    @match("table", "ChannelTitle", "0", "Name", ANY)
    def normalize_overlay_channel_name_text(self, tokens):
        yield self.make_media_streams_overlay_text(overlay_name="ChannelTitle", text=tokens[4])
