from grammar import grammar
from ..data import fetchData, TimeSeries


def evaluateTarget(requestContext, target):
    tokens = grammar.parseString(target)
    result = evaluateTokens(requestContext, tokens)

    if isinstance(result, TimeSeries):
        return [result]  # we have to return a list of TimeSeries objects

    return result


def evaluateTokens(requestContext, tokens):
    if tokens.expression:
        return evaluateTokens(requestContext, tokens.expression)

    elif tokens.pathExpression:
        return fetchData(requestContext, tokens.pathExpression)

    elif tokens.call:
        func = functions[tokens.call.funcname]
        args = [evaluateTokens(requestContext,
                               arg) for arg in tokens.call.args]
        kwargs = dict([(kwarg.argname,
                        evaluateTokens(requestContext, kwarg.args[0]))
                       for kwarg in tokens.call.kwargs])
        return func(requestContext, *args, **kwargs)

    elif tokens.number:
        if tokens.number.integer:
            return int(tokens.number.integer)
        elif tokens.number.float:
            return float(tokens.number.float)
        elif tokens.number.scientific:
            return float(tokens.number.scientific[0])

    elif tokens.string:
        return tokens.string[1:-1]

    elif tokens.boolean:
        return tokens.boolean[0] == 'true'


#Avoid import circularities
from ..functions import functions
