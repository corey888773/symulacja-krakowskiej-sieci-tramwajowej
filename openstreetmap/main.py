import urllib.request, urllib.error, os

bbox = 'w="19.88" s="50.01" e="20.13" n="50.11"' # krakow
query = '''
<osm-script output="json" timeout="25">
  <union>
    <query type="node">
      <has-kv k="railway" v="tram_stop"/>
      <bbox-query {BORDERBOX}/>
      </query>
    
    <query type="way">
      <has-kv k="railway" v="tram"/>
      <bbox-query {BORDERBOX}/>
      </query>
  </union>

  <print mode="body"/>
  <recurse type="down"/>
  <print mode="skeleton" order="quadtile"/>
</osm-script>
'''

curr_dir = os.path.dirname(os.path.abspath(__file__))

def main():
    data = query.replace("{BORDERBOX}", bbox)
    req = urllib.request.Request(
        url='http://overpass-api.de/api/interpreter',
        method='GET',
        headers={'Content-Type': 'text/plain'},
        data=data.encode('utf-8')
    )

    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')

            with open(f'{curr_dir}/open-street-map.json', 'w') as out_file:
                out_file.write(body)
    except urllib.error.HTTPError as e:
        print(e)
        print(e.read())

if __name__ == "__main__":
    main()