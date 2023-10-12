# weight Model Interface

Object's weight properties

| Name         | Type  | Description                             | Required  | Constant  | Default |
| ------------ | ----- | --------------------------------------- | --------- | --------- | ------- |
| weight       | Float | Own weight of object in kg              | {{ yes }} | {{ yes }} |         |
| is_recursive | Bool  | true - add to the weight of the object  |           |           |         |
|              |       | the weight of its modules (connected to | {{ yes }} | {{ yes }} | False   |
|              |       | connection direction `i`)               |           |           |         |
