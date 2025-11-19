import split
import generateEmbeddings

print("Beginnning Ingest...")

'''
paste directory of documentation into data_dir, 
for best results things should be organsed in folders.
currently the variable is set to the path on my laptop,
you MUST change this before running this code.
'''
data_dir = '/home/nick/Desktop/Projects/Formula-AI/Data' 

split.main(data_dir)
generateEmbeddings.main()

print("Ingest Completed :)")