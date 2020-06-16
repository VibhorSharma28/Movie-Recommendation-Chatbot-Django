from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.models import User, auth
from django.http import HttpResponse, Http404
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from chatterbot import ChatBot
import operator
import tmdbv3api as tb
from django.contrib.auth import login as auth_login
tmdb = tb.TMDb()
tmdb.api_key = 'ef9d09282b5ec0b221147c2cff9fe58d'
tmdb.language = 'en'
tmdb.debug = True
movie = tb.Movie()

@csrf_exempt
def get_response(request):
	response = {'status': None}

	if request.method == 'POST':
		data = json.loads(request.body.decode('utf-8'))
		message = data['message']
		stop_words = set(stopwords.words('english')) 
		word_tokens = word_tokenize(message)
		filtered_sentence = [w for w in word_tokens if not w in stop_words] 
		filtered_sentence = [] 
		for w in word_tokens: 
			if w not in stop_words: 
				filtered_sentence.append(w)  
		#filtered_sentence is the list of processed words in the query

		chat_response = "No keyword used/Invalid response."
		if 'popular' in filtered_sentence:
			movie =tb.Movie()
			popular = movie.popular()
			string=""
			for i in range(4):
				string+=popular[i].title+", "
			string+=popular[4].title #
			chat_response='Some popular movies right now are '+string

		genre_to_id={"ScienceFiction":878,"Drama":18,"Action":28,"Comedy":35,"Thriller":53,"Horror":27,"Romance":10749,"Fantasy":14,"History":46,"Adventure":12,"Mystery":9648}


		if 'genre' in filtered_sentence:
			discover=tb.Discover()
			i=filtered_sentence.index('genre')
			string=''
			for i in range(i+1,len(filtered_sentence)):
			  	string += filtered_sentence[i]
			string2=''
			if string in genre_to_id.keys():	
				a=genre_to_id[string]
				popular = discover.discover_movies({
			    "with_genres":a})
				for i in range(4):
					string2+=popular[i].title+", "
				string2+=popular[4].title
				chat_response="Some popular "+string+ " movies right now are "+string2
			else:
				chat_response="The query should be in the form of: \"suggest me some movie of genre g\" and g should be from the following: Science Fiction, Drama, Action, Comedy, Thriller, Horror, Romance, Fantasy, History, Adventure, Mystery"

		if 'kids' in filtered_sentence:
			discover = tb.Discover()
			popular = discover.discover_movies({
    		'certification_country': 'US',
    		'certification.lte': 'G',
    		'sort_by': 'popularity.desc'})
			string = ''
			for i in range(4):
				string+=popular[i].title+", "
			string+=popular[4].title
			chat_response='Some popular kids movies right now are '+string

		if 'review' in filtered_sentence:
	  		movie = tb.Movie()
	  		k=filtered_sentence.index('review')
	  		if 'movie' not in filtered_sentence[k:]:
	  			chat_response='The query should be in the form of: \"give review of movie x\"'
	  		else:
	  			i=filtered_sentence.index('movie')
		  		string=''
		  		for i in range(i+1,len(filtered_sentence)):
		  			string += filtered_sentence[i]
		  		string=string[:len(string)-1]
		  		search = movie.search(string)
		  		chat_response = movie.reviews(search[0].id)
		  		chat = chat_response[0].entries
		  		count=0
		  		chat_response=''
		  		for i in chat["content"]:
		  			if count!=300:
		  				chat_response+=i
		  				count+=1
		  			else:
		  				chat_response+=".... "+"\n\n For more check out: "+chat["url"]
		  				break

		if 'cast' in filtered_sentence:
			movie = tb.Movie()
			k=filtered_sentence.index('cast')
			if 'movie' not in filtered_sentence[k:]:
	  			chat_response='The query should be in the form of: \"cast of movie x\"'
			else:
				i=filtered_sentence.index('movie')
				string=''
				for i in range(i+1,len(filtered_sentence)):
					string += filtered_sentence[i]
				string=string[:len(string)-1]
				search = movie.search(string)
				chat_response = movie.credits(search[0].id)
				chat = chat_response.cast
				chat_response = "Starring:  "
				for i in chat:
					chat_response+=i["name"]+" as "+i["character"]+"  ||  "

		if 'popularity' in filtered_sentence:
	  		movie = tb.Movie()
	  		k=filtered_sentence.index('popularity')
	  		if 'movie' not in filtered_sentence[k:]:
	  			chat_response='The query should be in the form of: \"popularity of movie x\"'
	  		else:
	  			i=filtered_sentence.index('movie')
		  		string=''
		  		for i in range(i+1,len(filtered_sentence)):
		  			string += filtered_sentence[i]
		  		string=string[:len(string)-1]
		  		search = movie.search(string)
		  		chat_response=search[0].popularity

		if 'tell' in filtered_sentence:
	  		movie = tb.Movie()
	  		k=filtered_sentence.index('tell')
	  		if 'movie' not in filtered_sentence[k:]:
	  			chat_response='The query should be in the form of: \"tell about movie x\"'
	  		else:
	  			i=filtered_sentence.index('movie')
		  		string=''
		  		for i in range(i+1,len(filtered_sentence)):
		  			string += filtered_sentence[i]
		  		string=string[:len(string)-1]
		  		search = movie.search(string)
		  		chat_response=search[0].overview

		response['message'] = {'text': chat_response, 'user': False, 'chat_bot': True}
		response['status'] = 'ok'


	else:
		response['error'] = 'no post data found'
	return HttpResponse(json.dumps(response),content_type="application/json")


def home(request, template_name="home.html"):
	context = {'title': 'Movie Recommendation ChatBot'}
	return render_to_response(template_name, context)

def go_to_signup(request):
	return render(request,'sign_up.html',{})

def sign(request):
	if request.method == 'POST':
		fname = request.POST['first_name'];
		lname = request.POST['last_name'];
		uname = request.POST['username'];
		email = request.POST['email'];
		pass1 = request.POST['password1'];
		pass2 = request.POST['password2'];

		if pass1==pass2:
			if User.objects.filter(username=uname).exists():
				print('Username taken')
			elif User.objects.filter(email=email).exists():
				print("Email taken")
			else:
				user = User.objects.create_user(username=uname,password=pass1,email=email,first_name=fname,last_name=lname)
				user.save();
				print('User created')
				context = {
				'user':user
				}
				return render(request,'logged_in_home.html',context)
		else:
			print('Password not matching')
			return redirect('/go_to_signup')
	else:
		return render(request,'sign_up.html',{})

def cust_home(request):
	return render(request,'logged_in_home.html',{})

def login(request):
	if request.method == 'POST':
		uname = request.POST['username'];

		password = request.POST['pass'];

		user = auth.authenticate(username=uname,password = password)
		if user is not None:
			auth_login(request,user)
			context={
			'user':user
			}
			return render(request,'logged_in_home.html',context)
		else:
			return redirect('/login/')
	else:
		return render(request,'sign_up.html',{})

def catalogue(request):
	movie = tb.Movie()
	popular = movie.popular()
	cat={}
	for i in range(10):
		cat[popular[i].title[:27]] = popular[i].poster_path;
	context={
	'cat':cat
	}
	return render(request,'catalogue.html',context)

# def catalogue1(request):
# 	movie = tb.Movie()
# 	popular = movie.popular()
# 	pop_mov = []
# 	pop_mov_pos = []
# 	for i in range(10):
# 		pop_mov.append(popular[i].title[:27])
# 		pop_mov_pos.append(popular[i].poster_path)
# 	context={
# 	'ans':pop_mov,
# 	'poster':pop_mov_pos
# 	}
# 	return render(request,'catalogue1.html',context)

def catalogue1(request):
	movie = tb.Movie()
	popular = movie.popular()
	cat={}
	for i in range(10):
		cat[popular[i].title[:27]] = popular[i].poster_path;
	context={
	'cat':cat
	}
	return render(request,'catalogue1.html',context)

def personalized(request):
	discover = tb.Discover()
	movie = tb.Movie()
	if request.method == 'POST':
		var1 = request.POST['user_movie1']
		var2 = request.POST['user_movie2']
		var3 = request.POST['user_movie3']
		var4 = request.POST['user_movie4']
		var5 = request.POST['user_movie5']
		movie_list=[]
		search1 = movie.search(var1)
		search2 = movie.search(var1)
		search3 = movie.search(var1)
		search4 = movie.search(var1)
		search5 = movie.search(var1)
		var1 = search1[0].id
		var2 = search2[0].id
		var3 = search3[0].id
		var4 = search4[0].id
		var5 = search5[0].id
		movie_list.append(var1)
		if var2 not in movie_list:
			movie_list.append(var2)
		if var3 not in movie_list:
			movie_list.append(var3)
		if var4 not in movie_list:
			movie_list.append(var4)
		if var5 not in movie_list:
			movie_list.append(var5)
		genre_count={878:0,18:0,28:0,35:0,53:0,27:0,10749:0,14:0,46:0,12:0,9648:0}
		for i in movie_list:
		    m = movie.details(i)
		    genre_id=[]
		    for k in m.genres:
		    	genre_id.append(k["id"])
		    for j in genre_id:
		        if j in genre_count.keys():
		            genre_count[j]+=1
		genre_count = dict(sorted(genre_count.items(), key=operator.itemgetter(1),reverse=True))	
		all_counts=list(genre_count.values())
		top3_genres=[]
		for i in range(3):
		    for genre, count in genre_count.items():
		        if count == all_counts[i]:
		            top3_genres.append(genre)
		popular = discover.discover_movies({
		    'with_genres':top3_genres,
		    'sort_by': 'popularity.desc'})
		string = []
		poster = []
		rec = {}
		for i in range(5):
			rec[popular[i].title] = popular[i].poster_path
		# 	string.append(popular[i].title)
		# 	poster.append(popular[i].poster_path)
		# string.append(popular[4].title)
		# poster.append(popular[4].poster_path)

		context = {
		'rec':rec,
		#'poster':poster
		}
		return render(request,'personalized.html',context)
	else:
		return render(request,'personalized.html',{})