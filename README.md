## Abstract

Modern software development processes today are often conducted via Continuous Integration (CI), Continuous Delivery (CD) and Continuous Deployment (CD) for every iterative code change. These build, test, deploy, and monitor each committed code changes from a code repository and help reduce human intervention in the process from development to deployment. This leaves these CI/CD-machines at a critical point the software development and deployment process and a failure of the integrity of these machines could lead to safety or security issues of the produced software. With this work we will show how to use Trusted computing technologies in the form of remote attestation to mitigate this issue by enforcing a system state and policies on the CI/CD-machine and providing a proof of the enforcement of it with the deployed software. This also helps to reduce human intervention needed for having a trustworthy binary.

## Integrity Measurement Architecture 

TCG (Trusted Computing Group) describes “Trust” as “an entity
can be trusted if it always behaves in the expected manner for the
intended purpose” [[1]](https://github.com/harris012/extend-IMA-measurments/blob/master/bibliography-and-references.md#1). It has defined a set of standards that
explain how to take integrity measurements of a system and how
to store the measurement results securely in TPM (Trusted
Platform Module) for trust computing.

TPM is a separate hardware chip that has cryptographic engines,
secure storage and registers, namely PCR (Platform Configuration
Register). PCR is manipulated in a trustworthy manner through
the two operations: extend and quote operation. The former is
used for measurement while the latter for attestation, which will
be explained further in the following paragraphs.

