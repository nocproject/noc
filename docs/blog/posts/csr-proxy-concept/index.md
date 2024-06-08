---
date: 2023-11-03
authors: [dv]
description: >
    A streamlined scheme to generate SSL certificates for localhost
categories:
    - Tech
---
# CSR Proxying for Obtaining a Valid SSL Certificate for Software Evaluation
The proposed scheme, developed by Dmitry Volodin of [Gufo Labs][Gufo Labs], is designed for software publishers distributing software for **EVALUATION PURPOSES** and requiring a valid SSL certificate to allow users access to the web interface.

The proposed scheme offers a streamlined process for users by redirecting their browsers to a well-known entry point like `https://go.example.com:<port>/` immediately after installation. It eliminates the need for additional user steps and ensures the private key remains secure and is not shared with any external parties.

<!-- more -->
## The Challenge

Ensuring a seamless software evaluation process is essential, and we must prioritize user convenience. During the evaluation, we cannot impose the following demands on the user:

1. Mandate additional IT infrastructure, such as certificate authorities, DNS servers, or domain ownership.
2. Expect expertise in certificate signing processes and SSL setup.
3. Require relaxing the operating system's security settings.
4. Demand modifications to system configurations.

Furthermore, it is our duty to treat all user data as highly sensitive and safeguard it under all circumstances, whether during the evaluation phase or in production. Failing to adhere to these restrictions often leads to an unsuccessful evaluation and a negative user experience.

Traditionally, there are three common approaches to providing SSL certificates for software:

1. Supplying the private key and a certificate signed by a recognized certificate authority.
2. Generating a self-signed certificate as part of the installation process.
3. Delegating the certificate signing process to the user.
4. Signing the certificate on behalf of the user using ACME protocol.

Let's compare the approaches:

| Approach                                                                             | User Infrastructure Requirement                       | Competency in Certificate Signing and SSL Setup                                               | Security Impact                                                                                                                                       | User Data Protection                                                            | Ease of Use                                                                                        |
| ------------------------------------------------------------------------------------ | ----------------------------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **1. Provide a Private Key and Certificate from a Recognized Certificate Authority** | -                                                     | -                                                                                             | The private key is shared beetween the parties and considered compromissed                                                                            | The private key is shared between the parties.                                  | Convenient for the user, trusted certificates                                                      |
| **2: Generate a Self-Signed Certificate During Installation**                        | -                                                     | -                                                                                             | Non-goer now. Trusting the certificate requires system settings manipulations, may loose the system security, and requires the restart of the browser | Protects user data during transmission, doesn't guarantee software authenticity | Extremelly complex for users.                                                                      |
| **3: Delegate Certificate Signing to the User**                                      | -                                                     | Requires users to handle the certificate signing process, may not be user-friendly and costly | Depends on user's ability to generate and manage certificates securely                                                                                | Effectiveness depends on the user's expertise in certificate management         | Can be complex for users not familiar with certificate signing and SSL setup, potential for errors |
| **4: Signing the Certificate on Behalf of the User Using ACME Protocol**             | Requires an ACME-based signer service and DNS control | -                                                                                             | -                                                                                                                                                     | -                                                                               | -                                                                                                  |

**In summary:**

- **Approach 1** is not recommended due to security concerns.
- **Approach 2** is discouraged due to its complexity and the need for system setup.
- **Approach 3** requires SSL knowledge and can become expensive due to certificate authority fees.
- **Approach 4** demands additional infrastructure and may not be feasible for all users.

All of these approaches fall short of meeting the necessary requirements, highlighting the need to develop a new and more suitable solution.

## Key Participants

### Software Publisher

A party seeking to distribute software for evaluation purposes.

**Requirements**:
1. Must have control over a DNS zone (e.g., example.com).
2. Create a well-known Fully Qualified Domain Name (FQDN) (e.g., go.example.com).
3. Establish a glue NS record pointing to the *SIGNER* DNS, e.g., `go NS <ip>`.
4. Define a well-known CSR subject, such as `CN=go.example.com`.
5. Ensure the *SIGNER* service is operational or leased (details below).

### Installer

A software component responsible for installing and configuring the evaluated product.

**Requirements**:
1. Generate a private RSA key:

```
openssl genrsa -out <key> 4096
```

2. Create a CSR using the well-known **subject**:

```
openssl req -key <key path> -new -out <csr path> -subj <subject>
```

3. POST the CSR to the *SIGNER* using the well-known signer URL.
4. Receive the signed certificate and make it available for the HTTPS server.

### Signer

A service that can be installed or leased by the **publisher**.

**Components**:
- Simple DNS server capable of serving A and TXT records.
- A straightforward HTTP endpoint.

**Requirements**:
- Maintain an additional configuration table with columns for subject and appropriate DNS zones.

**Endpoint Logic**:
1. Accept a request with a CSR.
2. Parse the request and extract the subject.
3. Verify the subject against the configuration table and reject requests for unknown subjects.
4. Acquire a lock (separate per DNS zone).
5. Generate an ACME challenge using an ACME-protocol library.
6. Place the `_acme_challenge` record in the appropriate zone and apply the changes.
7. Verify the validity of `_acme_challenge`.
8. Perform an ACME request with DNS verification and obtain the certificate.
9. Release the lock (separate per DNS zone).
10. Send a response to the *Installer*.

Logs can be collected for additional impersonated analytics, which complies with GDPR regulations. Custom labels may be sent by the *Installer* based on the *Publisher's* preferences and can be used for additional traffic segmentation.

## Sequence Diagram

``` mermaid
sequenceDiagram
    participant Installer
    box Signer
    participant API
    participant DNS
    end
    participant ACME
    Installer->>Installer: Generate private RSA key
    Installer->>Installer: Create CSR
    Installer->>API: CSR sign request
    activate API
    API->>API: Validate CSR subject
    API->>API: Acquire lock
    API->>API: Generate ACME request
    API->>DNS: Set _acme_challenge TXT
    API->>DNS: Request _acme_challenge
    activate DNS
    DNS->>API: Current _acme_challenge
    deactivate DNS
    API->>ACME: Signing request
    activate ACME
    ACME->>DNS: Request _acme_challenge
    activate DNS
    DNS->>ACME: Current _acme_challenge
    deactivate DNS
    ACME->>API: Signed certificate
    deactivate ACME
    API->>Installer: Signed certificate
    deactivate API
```

## Implementation Details

From a *Publisher's* perspective, the implementation closely resembles the standard certificate generation process:

1. Generate a private key.
2. Create a certificate signing request.
3. Sign the certificate.

The role of the *Signer* is to serve as a CSR proxy, transferring part of its trust to the user's certificate. This trust-sharing mechanism is based on the shared subject and DNS zone control, effectively limiting the scope of trust to prevent any potential misuse.

## Copyright Notice

Copyright © 2023 by Dmitry Volodin of [Gufo Labs][Gufo Labs]. All rights reserved.
The protocol may be used in open-source software freely, while commercial use requires prior permission.

[Gufo Labs]: https://gufolabs.com/