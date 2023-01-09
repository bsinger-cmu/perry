*Security Information and Event Management*

## SysFlow
*Cloud-native system telemetry pipeline*

**Motivation**: Visibility into services and applications is critical for creating a strong security posture and reducing cybersecurity risks.

**Challenge**:
- Conventional perimeter monitoring offers limited coverage and visibility into workloads and attack kill chains, posing severe asymmetry challenges for defenders and impeding timely security analysis and response to resist known and emerging cyber threats.
- Pre-SysFlow solutions  
	- too low-level, generating massive amount of data and making it impractical and prohibitively expensive to store, process, and analyze.
	- suffer from unnecessary generalizations, overly complex to ingest and process in realtime.
	- lack support for concurrently tracking event provenance while being streamed alive.
	- largely fragmented and dominated by proprietary data models.

**Requirements**:
1. lightweight, non-intrusive event collection
2. a data representation that is open, nonredundant, compact, and capable of expressing essential system properties and behaviors.
3. a telemetry pipeline that supports 
	1. dense, long-term archival of system traces
	2. efficient reasoning over historical system behaviors
	3. linkages of system behaviors with processes, users and containers to enable data provenance and process control flow graphs on streaming data.

**Solution**:
SysFlow aggregates related system calls into compact summarizations that are time-bound and contain a vast number of carefully selected attributes and statistics, ideal for a wide variety of analytics and forensics.

[SysFlow + ELK](https://sysflow.io/2021/08/20/elk-integration.html)

### Nice language

> Specifically, the analytics framework provides an *extensible policy engine* that *ingests customizable security policies* described in a *declarative input language*, providing facilities for defining *higher-order logic expressions* that are checked against SysFlow records. 
> This allows practitioners to *easily define security and compliance policies* that can be deployed on a *scalable, out-of-the-box analysis toolchain* while supporting extensible programmatic APIs for the implementation of custom analytics algorithms—enabling *efforts to be redirected towards* developing and sharing analytics, rather than building support infrastructure for telemetry.

## NetFlow
Aggregates packets from network sessions into single records that contain the 5-tuple identifier of the sessions combined with volumetric information. NetFlow provides orders of magnitude compression over packet collection and has been a staple for network-based analytics for the past two decades.

NetFlow played a pivotal role in scaling network-based analytics by condensing packet information into a much smaller flow data; furthermore, Netflow was widely adopted by the community because it is an open source format, and simple to use.

## Gartner Magic Quadrant Report

-> [IBM QRadar](https://www.ibm.com/downloads/cas/RLXJNX2G)

## Security Onion

>Security Onion is a free and open platform for Network Security Monitoring (NSM) and Enterprise Security Monitoring (ESM). NSM is, put simply, monitoring your network for security related events. It might be proactive, when used to identify vulnerabilities or expiring SSL certificates, or it might be reactive, such as in incident response and network forensics.

