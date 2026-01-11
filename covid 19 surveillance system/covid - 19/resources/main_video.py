from pickle import FALSE
import cv2
from resources.simple_facerec import SimpleFacerec
from pymongo import MongoClient
from datetime import datetime
from pytz import timezone
import time

def suspect_name():
    client = MongoClient("")
    db = client.get_database("covid")
    attend_records = db.attendance
    suspect_records = db.suspect_details

    Date = datetime.now(timezone('Asia/Kolkata')).strftime("%Y-%m-%d")

    # Encode faces from a folder
    sfr = SimpleFacerec()
    sfr.load_encoding_images("suspects/")

    # Load Camera
    capture_duration = 30
    cap = cv2.VideoCapture(0)
    fgbg = cv2.createBackgroundSubtractorMOG2()
    start_time = time.time()
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    location = "C:\\Users\\Rinku\\Downloads\\login\\login\\static\\uploads\\suspection.mp4"
    out = cv2.VideoWriter(location, fourcc, 1,(640,480)) 

    while True:
        while( int(time.time() - start_time) < capture_duration ): 
            ret, frame = cap.read()

            face_locations, face_names = sfr.detect_known_faces(frame)
            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

                known_sus = list(attend_records.find({'suspect': 'true'}, {'name': 1}))
                unknown_sus = list(suspect_records.find({'sus_date': (Date)},{'name' : 1}))

                sus_list = []
                for item in known_sus:
                    a = item['name']
                    if a not in sus_list:
                        sus_list.append(a)

                for item in unknown_sus:
                    b = item['name']
                    if b not in sus_list:
                        sus_list.append(b)

                if name in sus_list or 'suspect' in sus_list:
                    suspection = 'suspect'
                    cv2.putText(frame, suspection, (x1, y1 - 10),cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4) 
                    if(ret==True):
                        out.write(frame)   
                        cv2.imshow("Frame", frame)
                        key = cv2.waitKey(1)
                        if key == 27:
                            break
                    else:
                        break

        cap.release()
        cv2.destroyAllWindows()
        return 

