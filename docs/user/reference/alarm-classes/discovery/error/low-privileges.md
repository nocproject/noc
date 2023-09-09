---
uuid: 1783626e-130f-4a5c-80ff-fbf7165f1fd3
---
# Discovery | Error | Low Privileges

Low privilege for executing command on managed object

## Symptoms

CLI command is not supported in current CLI mode and nothing password for raise permission level

## Probable Causes

Low permission level and not credential to raise it for execute command

## Recommended Actions

Add enable password to managed object settings or grant permission for execute commands

## Variables

Variable | Description | Default
--- | --- | ---
path | Path to alarms | {{ no }}
message | Error detail message | {{ no }}
