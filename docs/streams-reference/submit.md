# submit Stream
`submit` stream is a part of the [Orchestration Pipeline](index.md#orchestration-pipeline).
Messages are processed by [runner](../services-reference/runner.md) service.

## Subscribers

- [runner](../services-reference/runner.md) service.

## Message Headers

`submit` stream doesn't use additional headers.

## Message Format

`dispose` stream carries JSON-encoded messages of several types. The type of message is encoded
in the `$op` field. Unknown message types and malformed messages are discarded.

### submit message

`submit` messages represent a new job group request.

| Field              | Type                        | Description                                                                                                                                                      |
| ------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$op`              | String                      | Equals to `submit`                                                                                                                                               |
| `name`             | String                      | Job name, unique within job group (common parent)                                                                                                                |
| `action`           | String                      | Name of the action. Mutual exclusive with `jobs`                                                                                                                 |
| `description`      | String                      | Optional description.                                                                                                                                            |
| `labels`           | Array of String             | List of labels.                                                                                                                                                  |
| `allow_fail`       | Boolean                     | If set to true, `FAILED` job became `WARNING`                                                                                                                    |
| `locks`            | Array of String             | Optional list of lock names. Lock names are jinja2  template variables, in where environment is used as content.                                                 |
| `inputs`           | {{complex}} Array of Object | List of input mappigs.                                                                                                                                           |
| {{tab}} `name`     | String                      | Name of the input parameter, action-specific                                                                                                                     |
| {{tab}} `value`    | String                      | Parameter value. Jinja2 template in where the environment is used as context. If `job` parameter is set, the job result is exposed as `result` context variable. |
| {{tab}} `job`      | String                      | Optional job name.                                                                                                                                               |
| `require_approval` | Boolean                     | Job will be created in `PENDING` status                                                                                                                          |
| `depends_on`       | Array of String             | List of dependencies. Dependencies are  the names of the jobs from the same group. Circular dependensies are not allowed                                         |
| `environment`      | Object                      | Dict of evrironment variables and their values, available for same job and exposed to all children                                                               |
| `jobs`             | Array of Object             | List of nested jobs. Mutual exclusive with `actions`                                                                                                             |