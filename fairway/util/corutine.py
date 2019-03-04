
def limit(n_sims, gen):
    count = 0
    while count < n_sims:
        count += 1
        yield gen.__next__()


def coroutine(func):
    def wrapper(*args, **kw):
        gen = func(*args, **kw)
        gen.send(None)
        return gen
    return wrapper
