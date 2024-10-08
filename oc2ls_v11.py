from typing import Optional
from jadnschema.schema import Schema
from jadnschema.schema.info import Information
from jadnschema.schema.definitions import *
from pydantic import ConfigDict, Extra


# Primitive Types
DomainName = custom_def("Domain-Name", String, ["/hostname"], "[RFC1034], Section 3.5")
EmailAddr = custom_def("Email-Addr", String, ["/email"], "Email address - [RFC5322], Section 3.4.1")
IDNDomainName = custom_def("IDN-Domain-Name", String, ["/idn-hostname"], "Internationalized Domain Name - [RFC5890], Section 2.3.2.3")
IDNEmailAddr = custom_def("IDN-Email-Addr", String, ["/idn-email"], "Internationalized email address - [RFC6531]")
IRI = custom_def("IRI", String, ["/iri"], "Internationalized Resource Identifier, [RFC3987]")
MACAddr = custom_def("MAC-Addr", Binary, ["/eui"], "Media Access Control / Extended Unique Identifier address - EUI-48 or EUI-64 as defined in [EUI]")
URI = custom_def("URI", String, ["/uri"], "Uniform Resource Identifier, [RFC3986]")
DateTime = custom_def("Date-Time", Integer, ["{0"], "Date and Time")
Duration = custom_def("Duration", Integer, ["{0"], "A length of time")
Hostname = custom_def("Hostname", String, ["/hostname"], "Internet host name as specified in [RFC1123]")
IDNHostname = custom_def("IDN-Hostname", String, ["/idn-hostname"], "Internationalized Internet host name as specified in [RFC5890], Section 2.3.2.3")
IPv4Addr = custom_def("IPv4-Addr", Binary, ["/ipv4-addr"], "32 bit IPv4 address as defined in [RFC0791]")
IPv6Addr = custom_def("IPv6-Addr", Binary, ["/ipv6-addr"], "128 bit IPv6 address as defined in [RFC8200]")
Port = custom_def("Port", Integer, ["{0", "}65535"], "Transport Protocol Port Number, [RFC6335]")
Version = custom_def("Version", String,  [], "Major.Minor version number")
Namespace = custom_def("Namespace", String, ["/uri"], "Unique name of an Actuator Profile")
CommandID = custom_def("Command-ID", String, ["%^\\S{0,36}$"], "Command Identifier")

# Custom Types
Properties = custom_def("Properties", ArrayOf, ["*String", "{1", "q"], "A list of names that uniquely identify properties of an Actuator")
Features = custom_def("Features", ArrayOf, ["*Feature", "}10", "q"], "An array of zero to ten names used to query an Actuator for its supported capabilities")
Targets = custom_def("Targets", ArrayOf, ["*>Target", "{1", "}0", "q"], "List of Target types")
ActionTargets = custom_def("Action-Targets", MapOf, ["+Action", "*Targets", "{1"], "Map of each action supported by this actuator to the list of targets applicable to that action")


# Shared
class Payload(Choice):
    bin: Binary = Field(id=1, description="Specifies the data contained in the artifact")
    url: URI = Field(id=2, description="MUST be a valid URL that resolves to the un-encoded content")


class L4Protocol(Enumerated):
    """
    Value of the protocol (IPv4) or next header (IPv6) field in an IP packet. Any IANA value, [RFC5237]
    """
    class Values:
        icmp = Field("icmp", id=1, description="Internet Control Message Protocol - [RFC0792]")
        tcp = Field("tcp", id=6, description="Transmission Control Protocol - [RFC0793]")
        udp = Field("udp", id=17, description="User Datagram Protocol - [RFC0768]")
        sctp = Field("sctp", id=132, description="Stream Control Transmission Protocol - [RFC4960]")

    class Options:
        name = "L4-Protocol"


class Hashes(Map):
    """
    Cryptographic hash values
    """
    md5: Optional[Binary] = Field(id=1, options=["/x", "{16", "}16"], description="MD5 hash as defined in [RFC1321]")
    sha1: Optional[Binary] = Field(id=2, options=["/x", "{20", "}20"], description="SHA1 hash as defined in [RFC6234]")
    sha256: Optional[Binary] = Field(id=3, options=["/x", "{32", "}32"], description="SHA256 hash as defined in [RFC6234]")

    class Options:
        minv = 1


class File(Map):
    name_: Optional[String] = Field(alias="name", id=1, description="The name of the file as defined in the file system")
    path: Optional[String] = Field(id=2, description="The absolute path to the location of the file in the file system")
    hashes: Optional[Hashes] = Field(id=3, description="One or more cryptographic hash codes of the file contents")


class Process(Map):
    pid: Optional[Integer] = Field(id=1, options=["{0"], description="Process ID of the process")
    name_: Optional[String] = Field(alias="name", id=2, description="Name of the process")
    cwd: Optional[String] = Field(id=3, description="Current working directory of the process")
    executable: Optional[File] = Field(id=4, description="Executable that was executed to start the process")
    parent: Optional['Process'] = Field(id=5, description="Process that spawned this one")
    command_line: Optional[String] = Field(id=6, description="The full command line invocation used to start this process, including all arguments")


class IPv4Net(Array):
    """
    IPv4 address and prefix length
    """
    ipv4_addr: IPv4Addr = Field(id=1, description="IPv4 address as defined in [RFC0791]")
    prefix_length: Optional[Integer] = Field(id=2, description="CIDR prefix-length. If omitted, refers to a single host address")

    class Options:
        name = "IPv4-Net"
        format = "ipv4-net"


class IPv4Connection(Record):
    """
    5-tuple that specifies a tcp/ip connection
    """
    src_addr: Optional[IPv4Net] = Field(id=1, description="IPv4 source address range")
    src_port: Optional[Port] = Field(id=2, description="Source service per [RFC6335]")
    dst_addr: Optional[IPv4Net] = Field(id=3, description="IPv4 destination address range")
    dst_port: Optional[Port] = Field(id=4, description="Destination service per [RFC6335]")
    protocol: Optional[L4Protocol] = Field(id=5, description="Layer 4 protocol (e.g., TCP) - see L4-Protocol section")

    class Options:
        name = "IPv4-Connection"
        minv = 1


class IPv6Net(Array):
    """
    IPv6 address and prefix length
    """
    ipv6_addr: IPv6Addr = Field(id=1, description="IPv6 address as defined in [RFC8200]")
    prefix_length: Optional[Integer] = Field(id=2, description="prefix length. If omitted, refers to a single host address")

    class Options:
        name = "IPv6-Net"
        format = "ipv6-net"


class IPv6Connection(Record):
    """
    5-tuple that specifies a tcp/ip connection
    """
    src_addr: Optional[IPv6Net] = Field(id=1, description="IPv6 source address range")
    src_port: Optional[Port] = Field(id=2, description="Source service per [RFC6335]")
    dst_addr: Optional[IPv6Net] = Field(id=3, description="IPv6 destination address range")
    dst_port: Optional[Port] = Field(id=4, description="Destination service per [RFC6335]")
    protocol: Optional[L4Protocol] = Field(id=5, description="Layer 4 protocol (e.g., TCP) - [Section 3.4.2.10]")

    class Options:
        name = "IPv6-Connection"
        minv = 1


class Feature(Enumerated):
    """
    Specifies the results to be returned from a query features Command
    """
    class Values:
        versions = Field("versions", id=1, description="List of OpenC2 Language versions supported by this Actuator")
        profiles = Field("profiles", id=2, description="List of profiles supported by this Actuator")
        pairs = Field("pairs", id=3, description="List of supported Actions and applicable Targets")
        rate_limit = Field("rate_limit", id=4, description="Maximum number of Commands per minute supported by design or policy")
        args = Field("args", id=5, description="List of supported Command Argumemnts")


class Device(Map):
    hostname: Optional[Hostname] = Field(id=1, description="A hostname that can be used to connect to this device over a network")
    idn_hostname: Optional[IDNHostname] = Field(id=2, description="An internationalized hostname that can be used to connect to this device over a network")
    device_id: Optional[String] = Field(id=3, description="An identifier that refers to this device within an inventory or management system")


class Artifact(Record):
    mime_type: Optional[String] = Field(id=1, description="Permitted values specified in the IANA Media Types registry, [RFC6838]")
    payload: Optional[Payload] = Field(id=2, description="Choice of literal content or URL")
    hashes: Optional[Hashes] = Field(id=3, description="Hashes of the payload content")

    class Options:
        minv = 1


class Target(Choice):
    model_config = ConfigDict(extra='allow')
     
    artifact: Artifact = Field(id=1, description="An array of bytes representing a file-like object or a link to that object")
    command: CommandID = Field(id=2, description="A reference to a previously issued Command")
    device: Device = Field(id=3, description="The properties of a hardware device")
    domain_name: DomainName = Field(id=7, description="A network domain name")
    email_addr: EmailAddr = Field(id=8, description="A single email address")
    features: Features = Field(id=9, description="A set of items used with the query Action to determine an Actuator's capabilities")
    file: File = Field(id=10, description="Properties of a file")
    idn_domain_name: IDNDomainName = Field(id=11, description="An internationalized domain name")
    idn_email_addr: IDNEmailAddr = Field(id=12, description="A single internationalized email address")
    ipv4_net: IPv4Net = Field(id=13, description="An IPv4 address range including CIDR prefix length")
    ipv6_net: IPv6Net = Field(id=14, description="An IPv6 address range including prefix length")
    ipv4_connection: IPv4Connection = Field(id=15, description="A 5-tuple of source and destination IPv4 address ranges, source and destination ports, and protocol")
    ipv6_connection: IPv6Connection = Field(id=16, description="A 5-tuple of source and destination IPv6 address ranges, source and destination ports, and protocol")
    iri: IRI = Field(id=20, description="An internationalized resource identifier (IRI)")
    mac_addr: MACAddr = Field(id=17, description="A Media Access Control (MAC) address - EUI-48 or EUI-64 as defined in [EUI]")
    process: Process = Field(id=18, description="Common properties of an instance of a computer program as executed on an operating system")
    properties: Properties = Field(id=25, description="Data attribute associated with an Actuator")
    uri: URI = Field(id=19, description="A uniform resource identifier (URI)")

    # class Config:
    #     extra = 'allow'


class Action(Enumerated):
    class Values:
        scan = Field("scan", id=1, description="Systematic examination of some aspect of the entity or its environment")
        locate = Field("locate", id=2, description="Find an object physically, logically, functionally, or by organization")
        query = Field("query", id=3, description="Initiate a request for information")
        deny = Field("deny", id=6, description="Prevent a certain event or action from completion, such as preventing a flow from reaching a destination or preventing access")
        contain = Field("contain", id=7, description="Isolate a file, process, or entity so that it cannot modify or access assets or processes")
        allow = Field("allow", id=8, description="Permit access to or execution of a Target")
        start = Field("start", id=9, description="Initiate a process, application, system, or activity")
        stop = Field("stop", id=10, description="Halt a system or end an activity")
        restart = Field("restart", id=11, description="Stop then start a system or an activity")
        cancel = Field("cancel", id=14, description="Invalidate a previously issued Action")
        set = Field("set", id=15, description="Change a value, configuration, or state of a managed entity")
        update = Field("update", id=16, description="Instruct a component to retrieve, install, process, and operate in accordance with a software update, reconfiguration, or other update")
        redirect = Field("redirect", id=18, description="Change the flow of traffic to a destination other than its original destination")
        create = Field("create", id=19, description="Add a new entity of a known type (e.g., data, files, directories)")
        delete = Field("delete", id=20, description="Remove an entity (e.g., data, files, flows)")
        detonate = Field("detonate", id=22, description="Execute and observe the behavior of a Target (e.g., file, hyperlink) in an isolated environment")
        restore = Field("restore", id=23, description="Return a system to a previously known state")
        copy_ = Field("copy", alias="copy", id=28, description="Duplicate an object, file, data flow, or artifact")
        investigate = Field("investigate", id=30, description="Task the recipient to aggregate and report information as it pertains to a security event or incident")
        remediate = Field("remediate", id=32, description="Task the recipient to eliminate a vulnerability or attack point")


# Response
class ResponseType(Enumerated):
    class Values:
        none = Field("none", id=0, description="No response")
        ack = Field("ack", id=1, description="Respond when Command received")
        status = Field("status", id=2, description="Respond with progress toward Command completion")
        complete = Field("complete", id=3, description="Respond when all aspects of Command completed")

    class Options:
        name = "Response-Type"


class StatusCode(Enumerated):
    class Values:
        processing = Field("Processing", id=102, description="an interim Response used to inform the Producer that the Consumer has accepted the Command but has not yet completed it")
        ok = Field("OK", id=200, description="the Command has succeeded")
        created = Field("Created", id=201, description="the Command has succeeded and a new resource has been created as a result of it")
        badRequest = Field("Bad Request", id=400, description="the Consumer cannot process the Command due to something that is perceived to be a Producer error (e.g., malformed Command syntax)")
        unauthorized = Field("Unauthorized", id=401, description="the Command Message lacks valid authentication credentials for the target resource or authorization has been refused for the submitted credentials")
        forbidden = Field("Forbidden", id=403, description="the Consumer understood the Command but refuses to authorize it")
        notFound = Field("Not Found", id=404, description="the Consumer has not found anything matching the Command")
        internalError = Field("Internal Error", id=500, description="the Consumer encountered an unexpected condition that prevented it from performing the Command")
        notImplemented = Field("Not Implemented", id=501, description="the Consumer does not support the functionality required to perform the Command")
        serviceUnavailable = Field("Service Unavailable", id=503, description="the Consumer is currently unable to perform the Command due to a temporary overloading or maintenance of the Consumer")

    class Options:
        name = "Status-Code"
        id = True


class Results(Map):
    """
    Response Results
    """
    versions: Optional[Version] = Field(id=1, options=["q", "[0", "]10"], description="List of OpenC2 language versions supported by this Actuator")
    profiles: Optional[Namespace] = Field(id=2, options=["q", "[0", "]0"], description="List of profiles supported by this Actuator")
    pairs: Optional[ActionTargets] = Field(id=3, options=["[0"], description="List of targets applicable to each supported Action")
    rate_limit: Optional[Number] = Field(id=4, options=["y0.0", "[0"], description="Maximum number of requests per minute supported by design or policy")
    args: Optional[Enumerated] = Field(id=5, options=["#Args", "[0", "]0"], description="List of supported Command Arguments")


class OpenC2Response(Record):
    status: StatusCode = Field(id=1, description="An integer status code")
    status_text: Optional[String] = Field(id=2, description="A free-form human-readable description of the Response status")
    results: Optional[Results] = Field(id=3, description="Map of key:value pairs that contain additional results based on the invoking Command")

    class Options:
        name = "OpenC2-Response"


# Command
class Args(Map):
    start_time: Optional[DateTime] = Field(id=1, description="The specific date/time to initiate the Command")
    stop_time: Optional[DateTime] = Field(id=2, description="The specific date/time to terminate the Command")
    duration: Optional[Duration] = Field(id=3, description="The length of time for an Command to be in effect")
    response_requested: Optional[ResponseType] = Field(id=4, description="The type of Response required for the Command: none, ack, status, complete")


class Actuator(Choice):
    model_config = ConfigDict(extra='allow')
    # class Config:
    #     extra = 'allow'


class OpenC2Command(Record):
    """
    The Command defines an Action to be performed on a Target
    """
    action: Action = Field(id=1, description="The task or activity to be performed (i.e., the 'verb')")
    target: Target = Field(id=2, description="The object of the Action. The Action is performed on the Target")
    args: Optional[Args] = Field(id=3, description="Additional information that applies to the Command")
    actuator: Optional[Actuator] = Field(id=4, description="The subject of the Action. The Actuator executes the Action on the Target")
    command_id: Optional[CommandID] = Field(id=5, description="An identifier of this Command")

    class Options:
        name = "OpenC2-Command"


# Root Schema
class OpenC2LangV11(Schema):
    info = Information(
        package="http://oasis-open.org/openc2/oc2ls/v1.1",
        title="OpenC2 Language Profile",
        description="Language Profile from the OpenC2 Language Specification version 1.1",
        exports=["OpenC2-Command", "OpenC2-Response"]
    )
    types = {d.name: d for d in [
        OpenC2Command,
        OpenC2Response,
        Action,
        Target,
        Actuator,
        Args,
        Results,
        ActionTargets,
        Targets,
        StatusCode,
        Artifact,
        Device,
        DomainName,
        EmailAddr,
        Features,
        File,
        IDNDomainName,
        IDNEmailAddr,
        IPv4Net,
        IPv4Connection,
        IPv6Net,
        IPv6Connection,
        IRI,
        MACAddr,
        Process,
        Properties,
        URI,
        DateTime,
        Duration,
        Feature,
        Hashes,
        Hostname,
        IDNHostname,
        IPv4Addr,
        IPv6Addr,
        L4Protocol,
        Payload,
        Port,
        ResponseType,
        Version,
        Namespace,
        CommandID
    ]}
