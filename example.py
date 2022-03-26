from parcv import parcv
import timeit


start = timeit.default_timer()

parser = parcv.Parser(pickle=True, load_pickled=True)

json_output = parser.parse('cvs/emre sefer.pdf')
# print(json_output)

stop = timeit.default_timer()
print('Time: ', stop - start)  


# lines = parser.get_resume_lines()
# print(lines)

# segments = parser.get_resume_segments()
# print(segments)

file_name = "output.json"
parser.save_as_json(file_name)