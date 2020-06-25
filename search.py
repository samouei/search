#!/usr/bin/env python3

import pickle


def load_data(filename):
    """ Load actor/movie database """
    
    with open(filename, 'rb') as f:
        data = pickle.load(f)
        f.close()
    return data


def acted_together(data, actor_id_1, actor_id_2):
    """ Returns True if the two given actors 
    ever acted together in a film and False otherwise. """
    
    # If both actor IDs are in the tuple, they acted together
    for d in data:
        if (actor_id_1 in d) and (actor_id_2 in d):
            return True
    return False
 
    
def mapped_actors(data):
    """ 
    Creates a mapping of actors to whom they have acted with.
    Returns a dictionary of form {actor_id_1: {actor_id_2}}
    """ 
    
    d = {}
    
    # Map actor_1 to actor_2 and actor_2 to actor_1
    for i in data:
        if i[0] not in d:
            d[i[0]] = set() 
        d[i[0]].add(i[1])
        
        if i[1] not in d:
            d[i[1]] = set() 
        d[i[1]].add(i[0]) 
    return d


def actors_with_bacon_number(data, n):
    """ 
    Returns a Python set containing the ID numbers of all 
    the actors with that Bacon number n.
    """ 
    
    # Create a mapping of actors to whom they have acted with
    d = mapped_actors(data)

    
    # Run code for reasonable Bacon numbers only
    if n > len(d) - 1:
        return set()

    
    # Create Bacon's layer (Bacon numbers 0 and 1)    
    b_num_dic = {}
    b_num_dic[0], b_num_dic[1] = {4724}, d[4724]
    seen = b_num_dic[0] | b_num_dic[1]
    num = 1
    
    # Create a dictionary mapping Bacon numbers to actors 
    # (layer by layer starting B#1)
    while num <= n:
        b_num_dic[num + 1] = set()
        for actor in b_num_dic[num]:
            for a in d[actor]:
                if a not in seen:
                    b_num_dic[num + 1].add(a)
                    seen.add(a)
        num += 1
            
    return b_num_dic[n]

        
def construct_path(relation, start, end):
    """ 
    Constructs a path between two actors using a dictionary of child-parent 
    relationships. Returns a list with actor IDs.
    """ 
    
    path = [start]
    while end != start:
        path.append(relation[start])
        start = relation[start]
    path.reverse()
    return path

     
def bacon_path(data, actor_id):
    """ 
    Creates a list of actor IDs (any such shortest list if there are several) 
    detailing a "Bacon path" from Kevin Bacon to the actor denoted by actor_id. 
    If no path exists, returns None
    """ 
    
    Bacon = 4724
    return actor_to_actor_path(data, Bacon, actor_id)
            

def actor_to_actor_path(data, actor_id_1, actor_id_2):
    """ 
    Creates a list of actor IDs (any such shortest list if there are several) 
    detailing a path from the first actor to the second.
    """ 
    
    return actor_path(data, actor_id_1, lambda actor: actor == actor_id_2)
    

def actors_to_movie(data):
    """
    Creates a mapping between two actors and their shared movie.
    Returns a dictionary with the format {(actor_id_1, actor_id_2): movie_id}.
    """
    
    d = {}
    for i in data:
        d[(i[0], i[1])] = i[2]
        d[(i[1], i[0])] = i[2]
    return d


def get_movie_names(movie_data, movie_ids):
    """
    Creates movie names from movie IDs from a given database file path.
    Returns a list of movie names.
    """
    
    # Load database
    movies = load_data(movie_data)
    movie_names = []
    
    # Match movie ID with movie name
    for m in movie_ids:
        for k, v in movies.items():
            if v == m:
                movie_names.append(k)
    return movie_names

    
def movie_path(data, movie_database, actor_id_1, actor_id_2):
    """
    Determines movies that connect two arbitrary actors.
    Returns a list of movie names. 
    movie_database is a file path. 
    """
    
    # Create a mapping between two actors and their shared movie
    actors_to_movie_dic = actors_to_movie(data)
    
    # Creates a list of actor IDs connecting first actor to the second
    path = actor_to_actor_path(data, actor_id_1, actor_id_2)
    movies = []
    
    # Find the shared movie for each pair of actors
    for i in range(1, len(path)): 
        if (path[i - 1], path[i]) in actors_to_movie_dic:
            movies.append(actors_to_movie_dic[(path[i - 1], path[i])])
    
    return get_movie_names(movie_database, movies)
    
            
def actor_path(data, actor_id_1, goal_test_function):
    """
    Creates the shortest possible path from the given actor ID to 
    any actor that satisfies the goal test function. 
    Returns a a list containing actor IDs. 
    If no actors satisfy the goal condition, returns None.
    """
      
    agenda = {actor_id_1,} 
    seen = {actor_id_1,}
    relations = {}
    map_of_actors = mapped_actors(data)
  
    while agenda:
        
        # Get the children of the parent
        next_agenda = set()        
        for i in agenda:
            for j in map_of_actors[i]:
                if j not in seen and j not in agenda:
                    next_agenda.add(j)
                    
                    # Map child to parent
                    relations[j] = i
        
        # If actor satisfies function condition, return constructed path
        for id_ in agenda:
            if goal_test_function(id_):
                final_path = construct_path(relations, id_, actor_id_1)
                return final_path
        for next_ in agenda:
            if next_ not in seen:
                seen.add(next_)

        # Update agenda to next bacon number/layer
        agenda = next_agenda
            
    # No path exists
    return None


def actors_in_a_movie(data, film):
    """
    Finds all the actors in a movie.
    Returns a set of actor IDs.
    """
    
    # Create a mapping between actor pairs and their shared movie  
    actors_to_movie_dic = actors_to_movie(data) # dictionary {(actor_id_1, actor_id_2): film_id}
    actors_ids = set()

    # Get all the actors in movie 
    for actors, movie in actors_to_movie_dic.items():
        if movie == film:
            for a in actors: 
                actors_ids.add(a)  
    return actors_ids
    

def actors_connecting_films(data, film1, film2):
    """
    Finds the shortest possible list of actor ID numbers (in order) 
    that connect those two films.
    """
    
    # Get all the actors in movie 1 and 2
    film_1_actors = actors_in_a_movie(data, film1)
    film_2_actors = actors_in_a_movie(data, film2)     
    possible_paths = []    
    
    # Build paths          
    for actor in film_1_actors:
        possible_paths.append(actor_path(data, actor, lambda x: x in film_2_actors))
    
    # Return shortest path
    return min(possible_paths, key = len)
    


if __name__ == '__main__':

    pass
    
    #    2.2 Test: Testing the pickle load function
#    filename = 'resources/names.pickle'
#    mapped_data = load_data(filename)
#    print("The Python object type is:", type(mapped_data))
#    print(mapped_data)
#    name = "Barbara New"
#    ID = mapped_data[name]
#    print(f"{name}'s ID number is {ID}.")
#    for n,i in mapped_data.items(): 
#        if i == 142448:
#            print("ID number", i, "belongs to:", n) 
    
    #    Test tiny.pickle
#    filename = 'resources/tiny.pickle'
#    tiny_data = load_data(filename)
#    print(tiny_data)

    #    Test movies.pickle
#    filename = 'resources/movies.pickle'
#    movies = load_data(filename)
#    print(movies)
    
    #    3 Test: Testing acted_together
#    name_1 = "Ewa Froling"
#    name_2 = "Geena Davis"
#    name_1 = "David Clennon"
#    name_2 = "Barbra Rae"
#    filename = 'resources/names.pickle'
#    mapped_data = load_data(filename)
#    database = load_data('resources/small.pickle')
#    print(acted_together(database, mapped_data[name_1], mapped_data[name_2]))

    #    4 Test: Testing actors_with_bacon_number with Bacon number 6
    
#    filename = 'resources/large.pickle'
#    large_data = load_data(filename)  
#    names_filename = 'resources/names.pickle'
#    mapped_data = load_data(names_filename) 
#    b_num_6 = actors_with_bacon_number(large_data, 6)
#    b_num_6_names = {k for n in b_num_6 for k,v in mapped_data.items() if n == v}
##    b_num_6_names = set()
##    for n in b_num_6:
##        for k,v in mapped_data.items():
##            if n == v:
##                b_num_6_names.add(k)
#    print(f"Actors with Bacon number 6 are:\n{b_num_6_names}")

    #    5.1.1 Test: Testing bacon_path (Kevin Bacon to Fern Emmett)
    
#    filename = 'resources/large.pickle'
#    large_data = load_data(filename)  
#    names_filename = 'resources/names.pickle'
#    mapped_data = load_data(names_filename) 
#    path_ID = bacon_path(large_data, mapped_data['Fern Emmett'])
#    print("Path with actor IDs:", path_ID)
#    names = []
#    for n in path_ID:
#        for k,v in mapped_data.items():
#            if n == v:
#                names.append(k)
#    print("Path with actor names:", names)

    #    5.2 Test: Testing Bacon actor_to_actor_path (Linnea Hillberg to Jiang Wen)

#    filename = 'resources/large.pickle'
#    large_data = load_data(filename)  
#    names_filename = 'resources/names.pickle'
#    mapped_data = load_data(names_filename) 
#    path_ID = actor_to_actor_path(large_data, mapped_data['Linnea Hillberg'], mapped_data['Jiang Wen'])
#    print("Path with actor IDs:", path_ID)
#    names = []
#    for n in path_ID:
#        for k,v in mapped_data.items():
#            if n == v:
#                names.append(k)
#    print("Path with actor names:", names)        

    #    6 Test: Testing movie_path (Verna Bloom to Iva Ilakovac)
    
    filename = 'resources/large.pickle'
    movies_file_name = 'resources/movies.pickle'
    large_data = load_data(filename)  
    names_filename = 'resources/names.pickle'
    mapped_data = load_data(names_filename) 
    movies = movie_path(large_data, movies_file_name, mapped_data['Verna Bloom'], mapped_data['Iva Ilakovac'])
    print("Movie titles connecting Verna Bloom to Iva Ilakovac:\n",movies)


    

    
    
    
    
    
    
    