from parcv import parcv
import timeit


start = timeit.default_timer()


parser = parcv.Parser(pickle=True, load_pickled=True)

st = timeit.default_timer()
json_output = parser.parse('cvs/asem_cv.pdf')


stp = timeit.default_timer()
print('Time: ', stp - st)  

stop = timeit.default_timer()
print('All time: ', stop - start)  


# lines = parser.get_resume_lines()
# print(lines)

# segments = parser.get_resume_segments()
# print(segments)

file_name = "output.json"
parser.save_as_json(file_name)