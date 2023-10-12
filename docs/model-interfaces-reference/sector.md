# sector Model Interface

Antenna's sector, it is usually used in a combination about a [ModelInterface Geopoint](geopoint.md).

## Variables

| Name        | Type  | Description                      | Required  | Constant  | Default |
| ----------- | ----- | -------------------------------- | --------- | --------- | ------- |
| bearing     | float | Bearing angle                    | {{ yes }} | {{ no }}  |         |
| elevation   | float | Elevation angle                  | {{ yes }} | {{ no }}  | 0       |
| height      | float | Height above ground (in meters)  | {{ yes }} | {{ no }}  | 0       |
| h_beamwidth | float | Horizontal beamwidth (in angles) | {{ yes }} | {{ yes }} |         |
| v_beamwidth | float | Vertical beamwidth (in angles)   | {{ yes }} | {{ yes }} |         |
