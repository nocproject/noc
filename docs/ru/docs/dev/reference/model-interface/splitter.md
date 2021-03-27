---
62b945a4-ebf6-4174-94a7-c77e327d16d4
---

# splitter Model Interface

Split optical/electrical input power to outputs with given gain

## Variables

| Name   | Type   | Description                                                       | Required         | Constant   | Default   |
| ------ | ------ | ----------------------------------------------------------------- | ---------------- | ---------------- | --------- |
| split  | str    | Input power division, as comma-separated list of output_Name=gain | {{ yes }} | {{ yes }}       |           |

## Examples

splitter 1 to 2 with `50%/50%` attenuation optical/electrical power

    split: "out1=0.5,out2=0.5"

splitter 1 to 3 with `50%/25%/25%` attenuation optical/electrical power

    split: "out1=0.5,out2=0.25,out3=0.25"

splitter 1 to 2 with signal amplification twice up to 3dB

    split: "out1=2,out2=2"
