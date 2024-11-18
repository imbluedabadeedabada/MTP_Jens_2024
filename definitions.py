
IP = "192.168.0.119"
PORT = 9559
pepper_file_name = 'pepperzegt.txt'
default_start_position = (0.061603762209415436, 0.0630451887845993, 0.06797132641077042)
dict_obj_position = {"1":(-0.47630754113197327, 0.08082320541143417, 0.4018794000148773),
                    "2":(-0.35047054290771484, 0.0796777680516243, 0.4181469678878784),
                    "3":(-0.22605104744434357, 0.07874869555234909, 0.42973750829696655),
                    "4":(-0.10074947774410248, 0.07705161720514297, 0.4432786703109741),
                    "5":(0.03348568081855774, 0.07534623146057129, 0.4367918074131012),
                    "6":(0.16273309290409088, 0.07372288405895233, 0.44520941376686096),
                    "7":(0.3095007836818695, 0.07064922899007797, 0.4237704575061798),
                    "8":(0.4504513740539551, 0.06826087087392807, 0.43467026948928833),
                    "9":(0.5734785199165344, 0.06795012205839157, 0.43290409445762634)}

dict_objects = {"1": ("green", "square"),
                "2": ("orange", "triangle"),
                "3": ("green", "circle"),
                "4": ("orange", "square"),
                "5": ("purple", "triangle"),
                "6": ("orange", "circle"),
                "7": ("purple", "square"),
                "8": ("green", "triangle"),
                "9": ("purple", "circle")}

dict_map = {"1": ("B", "1"),
                "2": ("C", "2"),
                "3": ("A", "3"),
                "4": ("B", "2"),
                "5": ("A", "1"),
                "6": ("B", "3"),
                "7": ("C", "3"),
                "8": ("A", "2"),
                "9": ("C", "1")}

squares=[]
triangles=[]
circles=[]
greens=[]
oranges=[]
purples=[]
for k, v in dict_objects.items():
    if v[0] == "green":
        greens.append(k)
    elif v[0] == "orange":
        oranges.append(k)
    elif v[0] == "purple":
        purples.append(k)
    if v[1] == "square":
        squares.append(k)
    elif v[1] == "triangle":
        triangles.append(k)
    elif v[1] == "circle":
        circles.append(k)

if __name__ == '__main__':
    print("squares", squares)
    print("triangles", triangles)
    print("circles", circles)
    print("greens", greens)
    print("oranges", oranges)
    print("purples", purples)
    
