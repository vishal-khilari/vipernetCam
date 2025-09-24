# src/features.py
import pandas as pd, numpy as np, math

def bearing(lat1, lon1, lat2, lon2):
    y = math.sin(math.radians(lon2-lon1))*math.cos(math.radians(lat2))
    x = math.cos(math.radians(lat1))*math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))*math.cos(math.radians(lat2))*math.cos(math.radians(lon2-lon1))
    brng = math.degrees(math.atan2(y,x))
    return (brng + 360) % 360

def preprocess(path='data/simulated.csv', out='data/features.csv'):
    df = pd.read_csv(path, parse_dates=['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    df['lat_prev'] = df['latitude'].shift(1)
    df['lon_prev'] = df['longitude'].shift(1)
    df['time_prev'] = df['timestamp'].shift(1)
    R = 6371000
    dist=[]; dt=[]; br=[]
    for i,row in df.iterrows():
        if pd.isna(row['lat_prev']):
            dist.append(0.0); dt.append(1.0); br.append(0.0)
        else:
            phi1 = math.radians(row['lat_prev']); phi2 = math.radians(row['latitude'])
            dphi = math.radians(row['latitude'] - row['lat_prev']); dl = math.radians(row['longitude'] - row['lon_prev'])
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
            d = 2*R*math.asin(math.sqrt(a))
            dist.append(d)
            interval = (row['timestamp'] - row['time_prev']).total_seconds() or 1.0
            dt.append(interval)
            br.append(bearing(row['lat_prev'], row['lon_prev'], row['latitude'], row['longitude']))
    df['dist_m']=dist; df['dt_s']=dt; df['bearing']=br
    df['speed_kmph'] = df['dist_m']/1000 / (df['dt_s']/3600)
    df['bearing_prev'] = df['bearing'].shift(1)
    def turn_angle(r):
        if pd.isna(r['bearing_prev']): return 0.0
        diff = abs((r['bearing'] - r['bearing_prev'] + 180) % 360 - 180)
        return diff
    df['turn_angle'] = df.apply(turn_angle, axis=1)
    df['ang_vel'] = df['turn_angle'] / df['dt_s'].replace(0,1)
    df['hour'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute/60.0
    df['hour_sin'] = np.sin(2*np.pi*df['hour']/24); df['hour_cos'] = np.cos(2*np.pi*df['hour']/24)
    feats = df[['timestamp','latitude','longitude','speed_kmph','turn_angle','ang_vel','hour_sin','hour_cos','entry_zone']]
    feats.to_csv(out, index=False)
    print("Saved", out)
    return feats

if __name__=='__main__':
    preprocess()
