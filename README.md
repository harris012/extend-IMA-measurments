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

IMA is a Linux framework for system integrity verification that
follows the TCG standards [[2, 3]](https://github.com/harris012/extend-IMA-measurments/blob/master/bibliography-and-references.md#2). Figure 1 presents the overall
structure of IMA, consisting of three layers: measurement targets
(executables, LKMs (Loadable Kernel Modules) and files), IMA
mechanisms (measurement, remote attestation and appraisal), and
measurement results (Integrity measurement list and PCR extend). While booting, IMA measures all executables, LKMs and their
configuration files before execution. Taking a measurement of an
executable (or LKM or file) means computing a cryptographic hash of the executable such as SHA-1, SHA-512, and MD5. The
computed hashes are managed by a list, called as IML (Integrity
Measurement List). 
![Screenshot from 2023-01-09 02-09-29](https://user-images.githubusercontent.com/57041349/211228041-21db07a1-827b-4005-b7dd-54b0c15c4681.png)


