from cache import MemcachedInterface

def main():
    cache = MemcachedInterface()
    cache.set('foo', 'bar')
    print(cache.get('foo'))

if __name__ == '__main__':
    main()