# splitter Model Interface

Split optical/electrical input power to outputs with given gain

## Variables

<!-- table start -->
| Name | Type | Description | Required | Constant |
| --- | --- | --- | --- | --- |
| `split` | str | Input power division, as comma-separated list of output_name=gain | {{ yes }} | {{ yes }} |

<!-- table end -->

## Examples

splitter 1 to 2 with `50%/50%` attenuation optical/electrical power

    split: "out1=0.5,out2=0.5"

splitter 1 to 3 with `50%/25%/25%` attenuation optical/electrical power

    split: "out1=0.5,out2=0.25,out3=0.25"

splitter 1 to 2 with signal amplification twice up to 3dB

    split: "out1=2,out2=2"
