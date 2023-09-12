# python-docker-isolation-provider
Base use example:
async def fn(arg):
    data = arg['data']
    deep = arg['deep']
    result = f"Resolved data: {data}, {deep}"
    return result
