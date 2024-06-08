# Peering Management

The `Peering Management` module allows you to:

- Keep track of RPSL objects and their change history.
- Manage BGP sessions.
- Automatically or semi-automatically prepare and export up-to-date data to the RIR database.
- Build prefix lists based on entered data.
- Receive notifications about changes in the list of IP networks announced by clients.
- Add additional information to the incident card when classifying a BGP event.

## Configuration Procedure for the Module

The initial configuration includes filling in fields that correspond to those in the **RIPE DB**. Mandatory fields are highlighted in red. If any fields are missing, you can specify these parameters in the `Extra` field.

1. **Peering Management** - **Settings** - **Persons**:
   - Add all necessary objects with the type **Persons**.
   - Add all necessary objects with the type **Role** (noc, abuse, tech, etc.).

2. **Peering Management** - **Settings** - **Maintainers**:
   - Add Maintainers.

3. **Peering Management** - **Settings** - **Organizations**:
   - Add your organization(s). Specify `LIR` in the `Org. Type` if it is an LIR; otherwise, use `Other`.

4. **Peering Management** - **Settings** - **AS Profiles**:
   - Create the necessary profiles with different colors. These colors will be used to mark ASN in the list, for example, to visually differentiate between different subordinate organizations, etc.

## Configuration of Basic Parameters

1. **Peering Management** - **Settings** - **Peering Groups**:
   - Create all necessary groups that will be used to categorize our sessions, for example, `left` (uplinks), `right` (downlinks), etc. Here you can specify basic parameters that affect route priority and apply to the entire group.

2. **Peering Management** - **ASes**:
   - Add all your autonomous systems with which you will work. After adding, modifying, or deleting sessions with these ASes in **Peering Management** - **Peers**, you can generate a description for this object (AS) in RIPEDB. To do this, simply re-save the required AS and click the magnifying glass icon.

3. **Peering Management** - **Settings** - **Peering Points**:
   - Add all routers where you will establish BGP sessions (sessions you want to track). The checkbox `Enable Prefix-List Provisioning` enables the function of periodically querying prefixes for all entered sessions from the RIR database. If changes are detected, a notification is sent to the `Prefix-List Notification Group`. If there is no profile for the used router, select `Generic`.

4. **Peering Management** - **Communities** and **AS Sets**:
   - Add all your communities and AS-sets that you plan to use.

## Adding BGP Sessions

In the **Peering Management** - **Peers** section, add a new record with mandatory fields filled in as follows:

- **Peering Point** - The equipment on which the session will be created.
- **Peer Group** - The group type (Clients, Providers, etc.) of the session.
- **Project** - The contract number.
- **Local AS** - The local Autonomous System (AS) number.
- **Remote AS** - The remote AS number (the client's, provider's, or other side).
- **Status** - The planned status (e.g., active, planned activation, deactivated).
- **Local IP** - The local IP address on our side (with network mask).
- **Remote IP** - The remote IP address on the opposite side (with network mask).
- **Description** - You can specify a brief organization name for which the session is being set up. This field can be used in incident text templates.
- **RPSL Remark** - A brief organization name in lowercase using only Latin letters, numbers, hyphens (-), or underscores (_). This field is used for comments in RPSL ASN descriptions and can also be used in naming certain objects when configuring equipment using personal scripts or snippets.
- **Import Filter** - An AS-SET or Autonomous System number (e.g., `AS12345`) provided by the client to generate a list of their networks. If the session is not set up for a client, specify the name of the policy statement that will be used in this session.
- **Export Filter** - The name of the filter for outgoing announcements or an AS-SET on which the opposite side will build their filters.
- **Import Communities** - Specify traffic management communities separated by a space. For example, `RTK-3P` (if the router supports it in text form) or `65535:666`.
