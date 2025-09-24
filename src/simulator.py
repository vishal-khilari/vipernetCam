# src/simulator.py
import csv, random, math, datetime
def simulate_walk(start_lat, start_lon, n=500, step_mean_m=1.5):
    pts = [(start_lat, start_lon)]
    heading_prev = random.uniform(0,360)
    for i in range(1, n):
        prev_lat, prev_lon = pts[-1]
        heading = (heading_prev + random.gauss(0,25)) % 360
        step = max(0.2, random.gauss(step_mean_m, 0.6))
        dlat = (step/111320) * math.cos(math.radians(heading))
        dlon = (step/(111320*math.cos(math.radians(prev_lat)))) * math.sin(math.radians(heading))
        pts.append((prev_lat + dlat, prev_lon + dlon))
        heading_prev = heading
    return pts

def simulate_snake(start_lat, start_lon, n=200):
    pts=[]
    for i in range(n):
        x = i * 0.4
        lat = start_lat + 0.000005 * x
        lon = start_lon + 0.000005 * math.sin(x/2.0)
        pts.append((lat, lon))
    return pts

def generate_csv(path='data/simulated.csv'):
    start = (12.9340, 77.5120)
    normal = simulate_walk(*start, n=800, step_mean_m=1.2)
    snake = simulate_snake(start[0]+0.0005, start[1]+0.0005, n=150)
    pts = normal[:400] + snake + normal[400:]
    ts = datetime.datetime.utcnow()
    rows=[]
    prev = pts[0]
    for i,(lat,lon) in enumerate(pts):
        if i==0:
            speed = 0.0
            dt = 1.0
        else:
            # rough distance (meters)
            R=6371000
            phi1 = math.radians(prev[0]); phi2 = math.radians(lat)
            dphi = math.radians(lat - prev[0]); dl = math.radians(lon - prev[1])
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
            dist = 2*R*math.asin(math.sqrt(a))
            dt = random.uniform(0.8, 1.4)
            speed = (dist/1000) / (dt/3600)  # km/h
            prev = (lat, lon)
        direction = random.randint(0,359)
        zone = random.choice(['Zone_A','Zone_B','Zone_C'])
        rows.append([ (ts + datetime.timedelta(seconds=i)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                      lat, lon, round(speed,3), direction, zone ])
    with open(path,'w',newline='') as f:
        w = csv.writer(f)
        w.writerow(['timestamp','latitude','longitude','speed_kmph','direction_deg','entry_zone'])
        w.writerows(rows)
    print("Saved", path)

if __name__=='__main__':
    generate_csv()
