# Config Normalizer

`Normalizing` is the process of converting stream of input tokens,
received from `Tokenizer`, to the stream of output tokens,
representing ConfDB key's paths.

Normalizers are device-dependent and represent the translation
from device-depended tokenized config to abstract syntax of ConfDB.
Tokenizers do a lot of deal performing primal stream analysis and
applying configuration context, reducing complexity of normalizing.

Both `tokenizer` and `normalizer` works in single pipeline. Tokenizer
reads input stream and emits parsed tokens whenever they are ready.
Normalizer performs normalization and emits ConfDB syntax after
matching. Ability to work in pipelines greatly reduces memory
footprint of ConfDB processing, avoiding multiple copies of same data.



## Profile Integration

<!-- prettier-ignore -->
!!! todo

    Refer to Profile API

Following profile parameters are responsible for normalizer configuration:

**config_normalizer**

    String containing name of config normalizer to use. Contains
    normalizer class name. Normalizer must be subclass of :ref:`BaseNormalizer<dev-confdb-normalizer-api>`
    and must be located in the `noc.sa.profiles.X.Y.confdb.normalizer` module.

**config_normalizer_settings**

    Optional dict, containing config normalizer settings to be passed
    to Normalizer's constructor. Depends upon normalizer implementation.

**get_config_normalizer**(cls, object):

    Classmethod returning actual config normalizer name and its
    settings for selected managed object. Returns
    (`config_normalizer`, `config_normalizer_settings`) by default.
    Should be overriden in profile if normalizer or settings
    depends on platform or software version.

    :param object: ManagedObject reference
    :returns: tuple of (config tokenizer name, config tokenizer settings).
        Must return (None, None) if platform is not supported.



## Normalizer API

Normalizers must be subclass of `BaseNormalizer` and must be located
in profile's `confdb.normalizer` subpackage (`noc.sa.profiles.X.Y.confdb.normalizer`,
where `X.Y` is profile name).

<!-- prettier-ignore -->
!!! note

    Ensure the `sa/profiles/X/Y/confdb/__init__.py` file exists and empty.



#### Code boilerplate

Normalizer code boilerplate::

    # NOC modules
    from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST


    class MyNormalizer(BaseNormalizer):
        ...



#### @match decorator

Normalizer contains `generator functions` (python functions, containing
`yield` statement) annotated by `@match` decorators. Example::

    @match("no", "lldp")
    def normalize_no_lldp(self, tokens):

`@match` decorator compared to whole input tokens line. On full match
the generator function will be called passing all input tokens line
as `tokens` parameter. So example generator will be fired when
receiving `["no", "lldp"]` tokens and `tokens` parameter will contain
received tokens.

`@match` decorator may be applied several times upon same generator
function, allowing multiple matching variants. Example::

    @match("no", "lldp")
    @match("no", "lldp", "protocol")
    def normalize_no_lldp(self, tokens):

Will match `["no", "lldp"]` or `["no", "lldp", "protocol"]`.

Note, the match is `exact` for the whole line. Previous example will
not match the `["no", "lldp", "status"]` line.



#### @match macros

`@match` decorator allows to use one of following wildcard macros instead of exact string.
All macros must be imported from `noc.core.confdb.normalizer.base` module.


| Macro | Description                              |
| ----- | ---------------------------------------- |
| ANY   | Match any string in given position       |
|------ | ---------------------------------------- |
| REST  | Match all tokens to the rest of the line |


`tokens` parameter can be used to get real value of matched tokens::

    @match("interface", ANY, "description", REST)
    def normalize_inteface_description(self, tokens):
        if_name = tokens[1]
        description = " ".join(tokens[3:])
        ...

Multiple occurencies and various combination of macros are possible



#### Generator functions

Generator functions behind `@match` decorator must be python generators
containing at least one `yield` statement. Generator must yield tuples of
full paths of ConfDB syntax. Example::

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield "interfaces", tokens[2], "description", " ".join(tokens[3:])

Note that `yield` argument must be a tuple. Python treats comma-separated
values as tuples. So::

    "a", "b"

is a tuple. Multi-line tuples must be enclosed by brackets::

    ("a",
     "b")

For single-value tuples either of following variants may be used::

    tuple("abc")
    ("abc",)

Multiple `yield` statement are possible.

Note that Python 2.7 does not allow to mix `yield` and `return` in same function,
so `StopIteration` exception must be used to exit generator::

    ...
    def my_generator(....):
        ...
        raise StopIteration
        ...

`@match` generator must meet following rules:
* `yield` path *MUST* meet :ref:`ConfDB syntax<dev-confdb-syntax>`
* Interface names must be normalized by `interface_name` method (See API)
* Avoid to `yield` ConfDB paths directly, use syntax generators instead.

Syntax generators are defined in :ref:`ConfDB syntax<dev-confdb-syntax>`
and allow to inject named parameters to path. So our generator example
must be rewritten as::

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(
            interface=self.interface_name(tokens[2]),
            description=" ".join(tokens[3:])
        )



#### deferrable generators

In rare case single tokenized line does not contain all necessary information
and normalized line must be constructed from several lines. To handle
such cases `@match` generator may `yield` the `deferrable` expression.
`deferrable` is and partial expression bound to particular key. Different
`@match` generators may yield deferrable with same keys, refining necessary
parameters. When all prerequisitions are met, deferred call became
a real expression.

Consider following RouterOS config::

    /ip address
    add address=172.16.0.1/24 interface=bridge1 network=172.16.0.0

`routeros` tokenizer converts it to::

    ["/ip", "address", "0", "address", "172.16.0.1/24"]
    ["/ip", "address", "0", "interface", "bridge1"]
    ["/ip", "address", "0", "address", "172.16.0.0"]

As you can see, interface name and addresses are on different lines
(And there are reasons to deal it so). So normalizing is two step::

    @match("/ip", "address", INTEGER, "address", IPv4_PREFIX)
    def normalize_interface_address(self, tokens):
        yield self.defer(
            "ip.address.%s" % tokens[2],
            self.make_unit_inet_address,
            interface=deferrable("interface"),
            address=tokens[4]
        )

    @match("/ip", "address", INTEGER, "interface", ANY)
    def normalize_interface_address_interface(self, tokens):
        yield self.defer(
            "ip.address.%s" % tokens[2],
            interface=tokens[4]
        )

First generator yields deferrable with key `ip.address.0`. Zero is taken
from input tokens. Second parameter is the syntax generator to be called.
`interface` parameter is not known yet, so we denote it with `deferrable`
named `interface`. `address` parameter is known, so we attach it to deferrable.
Generator yields no output tokens, as deferrrable is not fully resolved.

Next generator will match interface part. Key `ip.address.0` is referred
to already known deferrable. So it attaches only `interface` parameter.
Generator lookups pending deferrables by keys and applies `interface` parameter.
As deferrable became fully resolved, it converts to actual
`make_unit_inet_address` and yield output tokens immediately.



#### Contexts

Sometimes is a good practice to set some flags, representing global
status, to alter behavior of following matches. Three methods
for context manipulation are available:

* `set_context`
* `get_context`
* `has_context`



#### Normalizer methods

**__init__**(self, param1=default1, .., paramN=defaultN)

    Constructor. Should be overriden if Normalizer accepts
    additional configuration from profile. Refer to `config_normalizer_settings` for details.

    :param param1: Custom configuration parameter #1 with default value
    :param paramN: Custom configuration parameter #N with default value

**set_context**(self, name, value)

    Set context flag `name` to `value`

    :param name: String containing flag name
    :param value: Flag value
    :returns: None

**get_context**(self, name, default=None)

    Get context flag `name`, returning its value or `default`

    :param name: String containing flag name
    :param default: Default value
    :returns: Key value or `default` if key not found

**has_context**(self, name)

    Check context has flag `name`

    :param name: String containing flag name
    :returns: True if context has key `name`, False otherwise

**interface_name**(self, *args)

    Convert interface name using profile's `convert_interface_name` method

    :param *args: Parts of interface name
    :returns: String containing normalized interface name

**to_prefix**(self, address, netmask)

    Convert IPv4 address and netmask to prefix form (`address/bits`

    :param address: IPv4 address
    :param netmask: IPv4 netmask
    :returns: IP address in prefix form

**defer**(context, gen=None, **kwargs)

    Create deferable with name `context`. Return actual `gen`
    call when all prerequisites are met.

    :param context: Name of deferable context
    :param gen: ConfDB syntax generator callable
    :param kwargs: syntax generator parameters, may contain `deferrable`
