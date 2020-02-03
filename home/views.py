from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Create your views here.
def home_view(request,*args,**kwargs):
	context={
		'travel' : readcsv('Travel'),
		'mystery' : readcsv('Mystery, Thriller & Suspense'),
		'scifi' : readcsv('Science Fiction & Fantasy'),
		'arts' : readcsv('Arts & Photography'),
		'literature' : readcsv('Literature & Fiction'),
		'sports' : readcsv('Sports & Outdoors'),
		'computer' : readcsv('Computers & Technology'),
		'humor' : readcsv('Humor & Entertainment')
	}
	return render(request,'index.html',context)



def about_view(request,*args,**kwargs):
	return render(request,'about.html',{})	


def contact_view(request,*args,**kwargs):
	return render(request,'contact.html',{})


def readcsv(category):
	maximum = 0
	ISBN =''
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'
	RATING_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalrating.csv'
	with open(BOOK_SRC, 'r') as book_file:
		with open(RATING_SRC, 'r') as rating_file:
			book = pd.read_csv(book_file)
			ratings = pd.read_csv(rating_file)
			categorybook = book.loc[book['CATEGORY']==category]
			merged = pd.merge(categorybook,ratings,on=['ISBN'])
			rating_count = pd.DataFrame(merged.groupby('ISBN')['bookRating'].count())
			rating_count1 = rating_count.sort_values('bookRating',ascending=False).head()
			average_rating=pd.DataFrame(merged.groupby('ISBN')['bookRating'].mean())
			average_rating['ratingCount']=pd.DataFrame(merged.groupby('ISBN')['bookRating'].count())
			averageRating = average_rating.sort_values('ratingCount',ascending=False).head()
			AVERAGE_RATING_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/avgRating.csv'
			with open(AVERAGE_RATING_SRC,'w') as avg_file:
				averageRating.to_csv(avg_file)
			with open(AVERAGE_RATING_SRC, 'r') as average_rating_file:
				avg = pd.read_csv(average_rating_file)
				print(avg)
				for i,row in avg.iterrows():
					#print(row)
					average_value = row['bookRating']
					if(average_value>maximum):
						maximum = average_value
						ISBN = row['ISBN']
						index = book.index.get_loc(book.index[book['ISBN'] == ISBN][0])
						img_url = book.loc[index]['IMAGE URL'] 
				print(img_url)		
			print(maximum)
			return img_url		



def recommend_view(request,*args,**kwargs):
	#Initialization
	recommended_category = ""
	img_url_list = []
	title = []
	ISBN_list = []
	dropdown1 = ''
	if request.GET.get('query'):
		dropdown1 = request.GET.get('query')
		print(dropdown1)
	else:
		dropdown1 = "popular"	
	if request.GET.get('query_name'):
		recommended_category = request.GET.get('query_name')
		print(recommended_category)
	else:
		recommended_category = "All"	
	#If popularity filtering is selected
	if dropdown1 == "popular":
		img_url_list,title,ISBN_list = recommend_popular(recommended_category)
		print(img_url_list)
		print("_________________________")
		print(title)
		print("_________________________")
		print(ISBN_list)
	elif dropdown1 == "personalized":
		img_url_list = recommend_personalized(recommended_category)
	recommend_context = {
		"img_list" : img_url_list,
		"title" : title,
		"ISBN" : ISBN_list
	}
	return render(request,'product.html',recommend_context)	



def recommend_popular(recommended_category):
	recommended_category_final = ""
	recommend_category_final = recommend_category_return(recommended_category)
	print("inside recommend_popular(recommended_category) "+recommend_category_final)																										
	#if recommend_category == "All":
	img_url_list,title,ISBN_list = recommend_popular_books(recommend_category_final)
	print(img_url_list)
	return img_url_list,title,ISBN_list



def music_view(request,*args,**kwargs):
	ISBN = ''
	index = 0
	music_list = []
	cosine_similarities = []
	ISBN = request.GET.get('query')
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'
	with open(BOOK_SRC, 'r') as book_file:
		book = pd.read_csv(book_file,sep=',')
		index = book.index.get_loc(book.index[book['ISBN'] == ISBN][0])
	print(index)	
	music_list = recommendMusic(index)
	print("---------------------))))))))00000000000000000000")
	print(music_list)	
	#if music_list[0] == 'Invalid':
	#	music_list[0] = "Can't Recommend music"
	#Get information of a book
	title,author,category,img = getInfo(ISBN)
	#recommend(345282256,7)
	recommend_context = {
		"title" : title,
		"author" : author,
		"category" : category,
		"img" : img,
		"music_list" : music_list
	}
	return render(request,'music.html',recommend_context)


#below code 'function item(id)' returns a row matching the id along with Book Title. Initially it is a dataframe, then we convert it to a list
def item(id):
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'
	with open(BOOK_SRC, 'r') as book_file:
		book = pd.read_csv(book_file,sep=',')
		return book.loc[ds1['ISBN'] == id]['TITLE'].tolist()[0]


def recommend(id, num):
	results = {} # dictionary created to store the result in a dictionary format (ID : (Score,item_id))
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'
	with open(BOOK_SRC, 'r') as book_file:
		book = pd.read_csv(book_file,sep=',')
		tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words='english')
		######ngram (1,3) can be explained as follows#####
		#ngram(1,3) encompasses uni gram, bi gram and tri gram
		#consider the sentence "The ball fell"
		#ngram (1,3) would be the, ball, fell, the ball, ball fell, the ball fell
		tfidf_matrix = tf.fit_transform(book['TITLE'])
		cosine_similarities = cosine_similarity(tfidf_matrix,tfidf_matrix)
		pd.set_option('display.max_colwidth', -1)
		for idx, row in book.iterrows(): #iterates through all the rows
			#the below code 'similar_indice' stores similar ids based on cosine similarity. sorts them in ascending order. [:-5:-1] is then used so that the indices with most similarity are got. 0 means no similarity and 1 means perfect similarity
			similar_indices = cosine_similarities[idx].argsort()[:-5:-1] #stores 5 most similar books, you can change it as per your needs
			print("inside"+str(similar_indices))
			similar_items = [(cosine_similarities[idx][i], book['ISBN'][i]) for i in similar_indices]
			print("similar items are : "+str(similar_items[1:]))
			results[row['ISBN']] = similar_items[1:]
			print(results)
	if (num == 0):
		print("Unable to recommend any book as you have not chosen the number of book to be recommended")
	elif (num==1):
		print("Recommending " + str(num) + " book similar to " + item(id))
	else :
		print("Recommending " + str(num) + " books similar to " + item(id))
	print("----------------------------------------------------------")
	recs = results[id][:num]
	for rec in recs:
		print("(((((((((((((((((((())))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))")
		print("You may also like to read: " + item(rec[1]) + " (score:" + str(rec[0]) + ")")	



def recommend_popular_books(category):
	ISBN =''
	img_url_list = []
	title_list = []
	ISBN_list = []
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'
	RATING_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalrating.csv'
	with open(BOOK_SRC, 'r') as book_file:
		with open(RATING_SRC, 'r') as rating_file:
			book = pd.read_csv(book_file)
			ratings = pd.read_csv(rating_file)
			if category == "All":
				categorybook = book
			else:	
				categorybook = book.loc[book['CATEGORY']==category]
				print(categorybook)
			#Merge book data and ratings data
			merged = pd.merge(categorybook,ratings,on=['ISBN'])
			print(merged)
			#how many users have rated to a particular book
			rating_count = pd.DataFrame(merged.groupby('ISBN')['bookRating'].count())
			#sort the rating count in descending order thus we will get the books which are rated by large no. of users
			rating_count1 = rating_count.sort_values('bookRating',ascending=False).head()
			print(rating_count1)
			#get the mean of ratings given by different users to a particular book
			average_rating=pd.DataFrame(merged.groupby('ISBN')['bookRating'].mean())
			#how many users have rated to a particular book(save count in column named 'ratingCount')
			average_rating['ratingCount']=pd.DataFrame(merged.groupby('ISBN')['bookRating'].count())
			#sort in descending order
			averageRating = average_rating.sort_values('ratingCount',ascending=False).head(12)
			AVERAGE_RATING_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/avgRating.csv'
			with open(AVERAGE_RATING_SRC,'w') as avg_file:
				averageRating.to_csv(avg_file)
			with open(AVERAGE_RATING_SRC, 'r') as average_rating_file:
				avg = pd.read_csv(average_rating_file,sep=',')
				print(avg)
				for i,row in avg.iterrows():
					#print(row)
					average_value = row['bookRating']
					ISBN = row['ISBN']
					index = book.index.get_loc(book.index[book['ISBN'] == ISBN][0])
					img_url = book.loc[index]['IMAGE URL']
					title = book.loc[index]['TITLE']
					ISBN = book.loc[index]['ISBN']
					img_url_list.append(img_url)
					title_list.append(title)
					ISBN_list.append(ISBN)
				return img_url_list,title_list,ISBN_list


def getInfo(isbn):
	title = ''
	author = ''
	category = ''
	img = ''
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'	
	with open(BOOK_SRC, 'r') as book_file:
		book = pd.read_csv(book_file)
		index = book.index.get_loc(book.index[book['ISBN'] == isbn][0])
		title = book.loc[index]['TITLE']
		author = book.loc[index]['AUTHOR']
		category = book.loc[index]['CATEGORY']
		img = book.loc[index]['IMAGE URL']
	return title,author,category,img



def recommendMusic(book_index):
    category = ""
    index=int(book_index)
    print(book_index)
    if index>=0 and index<=3022 :
    	print('--------------------------------')
    	print('comic')
    	category = 'Comics & Graphic Novels'
    elif index>=3023 and index<=5922 :
    	print('--------------------------------')
    	print('Test Preparation')
    	category = 'Test Preparation'
    elif index>=5923 and index<=7918 :
    	print('--------------------------------')
    	print('Mystery, Thriller & Suspense')
    	category = 'Mystery, Thriller & Suspense'        
    elif index>=7919 and index<=11712:
    	print('--------------------------------')
    	print('Science Fiction & Fantasy')
    	category = 'Science Fiction & Fantasy'
    elif index>=11713 and index<=15995 :
    	print('--------------------------------')
    	print('romance')
    	category = 'Romance'
    elif index>=15996 and index<=22877 :
    	print('--------------------------------')
    	print('Humor & Entertainment')
    	category = 'Humor & Entertainment'
    elif index>=22878 and index<=30432 :
    	print('--------------------------------')
    	print('Literature & Fiction')
    	category = 'Literature & Fiction' 
    elif index>=30433 and index<=33100 :
    	print('--------------------------------')
    	print('Engineering & Transportation')
    	category = 'Engineering & Transportation' 
    elif index>=33101 and index<=41891 :
    	print('--------------------------------')
    	print('Cookbooks, Food & Wine')
    	category = 'Cookbooks, Food & Wine'
    elif index>=41892 and index<=51801 :
    	print('--------------------------------')
    	print('Crafts, Hobbies & Home')
    	category = 'Crafts, Hobbies & Home'
    elif index>=51802 and index<=58253 :
    	print('--------------------------------')
    	print('Arts & Photography')
    	category = 'Arts & Photography'
    elif index>=58254 and index<=59916 :
    	print('--------------------------------')
    	print('Education & Teaching')
    	category = 'Education & Teaching'
    elif index>=59917 and index<=62432 :
        print('Parenting & Relationships')
        category = 'Parenting & Relationships'
    elif index>=65132 and index<=73102 :
        print('Computers & Technology')
        category = 'Computers & Technology'
    elif index>=73103 and index<=85168 :
        print('Medical Books')
        category = 'Medical Books'
    elif index>=85169 and index<=94425 :
        print('Science & Math')
        category = 'Science & Math'  
    elif index>=94426 and index<=106288 :
        print('Health, Fitness & Dieting')
        category = 'Health, Fitness & Dieting'
    elif index>=106289 and index<=116241 :
        print('Business & Money')
        category = 'Business & Money'
    elif index>=116242 and index<=123534 :
        print('Law')
        category = 'Law'
    elif index>=123535 and index<=127789 :
        print('Biographies & Memoirs')
        category = 'Biographies & Memoirs'
    elif index>=11713 and index<=15995 :
        print('History')
        category = 'History'
    elif index>=134583 and index<=137976:    
        category = 'Politics & Social Sciences'
    elif index>=137977 and index<=141239:    
        category = 'Reference'
    elif index>=141240 and index<=150363:    
        category = 'Christian Books & Bibles'
    elif index>=150364 and index<=157908:    
        category = 'Religion & Spirituality'                                                                                
    elif index>=157909 and index<=163866:    
        category = 'Sports & Outdoors'
    elif index>=163867 and index<=171335:    
        category = 'Teen & Young Adult'
    elif index>=171336 and index<=184897:    
        category = 'Children\'s Books'
    elif index>=184898 and index<=203157:    
        category = 'Travel'            
    switcher = { 
        'Comics & Graphic Novels': comicGraphic,
        'Science Fiction & Fantasy': fiction,
        'Travel': travel,
        'Romance':romance,
        'Humor & Entertainment' : humor,
        'Literature & Fiction' : literature,
        'Cookbooks, Food & Wine' : cookbooks,
        'Crafts, Hobbies & Home' : crafts,
        'Mystery, Thriller & Suspense':mystery,
        'Religion & Spirituality':religion,
        'Health, Fitness & Dieting':health
    }
    print(category)
    func=switcher.get(category,lambda :'Invalid')
    return func()	
    

def comicGraphic():
	track_list = []
	file_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' calmness']==1 	and row[' power']==1):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list    	
            

def travel():
	track_list = []
	print('inside travel')
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' amazement']==1 and row[' power']==1 and row[' joyful_activation']==1 and row[' calmness']==1 and row[' solemnity']==1 and row[' tension']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list
            
def fiction():
	track_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' amazement']==1 and row[' calmness']==1 and row[' tenderness']==0 and row[' nostalgia']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list 
            
def mystery():
	track_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		print('inside mystery')
		for i,row in music.iterrows():
			if(row[' amazement']==1 and row[' solemnity']==1 and row[' power']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list
            
def romance():
	track_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		print('inside romance')
		for i,row in music.iterrows():
			if(row[' tenderness']==1 and row[' nostalgia']==1 and row[' amazement']==0 and row[' power']==0 and row[' joyful_activation']==0 and row[' calmness']==0 and row[' tension']==0 and row[' solemnity']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list

            	
def religion():
	track_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		print('inside religion')
		for i,row in music.iterrows():
			if(row[' calmness']==1 	and row[' power']==1 and row[' tenderness']==0 and row[' tension']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list


def humor():
	track_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		print('inside religion')
		for i,row in music.iterrows():
			if(row[' calmness']==1 	and row[' power']==1 and row[' tenderness']==0 and row[' tension']==0 and row[' joyful_activation']==1 and row[' sadness']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list	    	


def health():
	track_list = []
	file_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' amazement']==0 and row[' power']==1 and row[' joyful_activation']==1 and row[' calmness']==1 and row[' solemnity']==1 and row[' tension']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list


def literature():
	track_list = []
	file_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' amazement']==1 and row[' calmness']==0 and row[' solemnity']==0):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list


def cookbooks():
	track_list = []
	file_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' solemnity']==0 and row[' tenderness']==0 and row[' tension']==0 and row[' calmness']==1 and row[' sadness']==0 and row[' nostalgia']==0 and row[' joyful_activation']==1):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list		


def crafts():
	track_list = []
	file_list = []
	MUSIC_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/music2.csv'	
	with open(MUSIC_SRC, 'r') as music_file:
		music = pd.read_csv(music_file)
		for i,row in music.iterrows():
			if(row[' solemnity']==0 and row[' tenderness']==0 and row[' tension']==0 and row[' calmness']==1 and row[' sadness']==0 and row[' nostalgia']==1 and row[' joyful_activation']==1):
				track_list.append("/media/"+str(row['track id'])+".mp3")
	return track_list	

"""def recommend_personalized():
	RATING_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalrating.csv'
	BOOK_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/finalbook.csv'
	MATRIX_SRC = '/home/dhanashree/MyFolder/Dev/trydjango/MusicRecommendation/home/matrix.csv'
	with open(RATING_SRC, 'r') as rating_file:
		ratings = pd.read_csv(rating_file)
		#count how many times a rating occur in a dataset
		countsr=ratings['bookRating'].value_counts()
		#delete rows with 0 ratings
		rating_zero = rating2.drop(rating2.loc[rating2['bookRating']==0].index)
		#select first 500 rows
		rating_selection=rating4.loc[1:500]
		#Create matrix with index as userID and columns as ISBN
		rating_pivot = rating3.pivot(index='userID',columns='ISBN').bookRating
		userID = rating_pivot.index
		ISBN = rating_pivot.columns
		print(rating_pivot.shape)
		#Fill nan values in matrix with 0
		rating_pivot = rating_pivot.fillna(0)
		with open(MATRIX_SRC,'w') as matrix_file:
			rating_pivot.to_csv('matrix.csv')"""
			



#function which returns selected recommendation_categort
def recommend_category_return(recommend_category):
	if recommend_category == "All":
		recommend_category_final = "All"
	elif recommend_category == "Comics":
		recommend_category_final = "Comics & Graphic Novels"
	elif recommend_category == "Mystery":
		recommend_category_final = "Mystery, Thriller & Suspense"
	elif recommend_category == "Science":
		recommend_category_final = "Science Fiction & Fantasy"
	elif recommend_category == "Love":
		recommend_category_final = "Romance"
	elif recommend_category == "Humor":
		recommend_category_final = "Humor & Entertainment"
	elif recommend_category == "Literature":
		recommend_category_final = "Literature & Fiction"
	elif recommend_category == "Cookbooks":
		recommend_category_final = "Cookbooks, Food & Wine"
	elif recommend_category == "Crafts":
		recommend_category_final = "Crafts, Hobbies & Home"
	elif recommend_category == "Arts":
		recommend_category_final = "Arts & Photography"
	elif recommend_category == "Education":
		recommend_category_final = "Education & Teaching"
	elif recommend_category == "Test":
		recommend_category_final = "Test Preparation"	
	elif recommend_category == "Parenting":
		recommend_category_final = "Parenting & Relationships"
	elif recommend_category == "Self-Help":
		recommend_category_final = "Self-Help"
	elif recommend_category == "Computers":
		recommend_category_final = "Computers & Technology"
	elif recommend_category == "Medical Books":
		recommend_category_final = "Medical Books"
	elif recommend_category == "ScienceMath":
		recommend_category_final = "Science & Math"
	elif recommend_category == "Health":
		recommend_category_final = "Health, Fitness & Dieting"
	elif recommend_category == "Business":
		recommend_category_final = "Business & Money"
	elif recommend_category == "Law":
		recommend_category_final = "Law"
	elif recommend_category == "Biographies":
		recommend_category_final = "Biographies & Memoirs"
	elif recommend_category == "History":
		recommend_category_final = "History"
	elif recommend_category == "Politics":
		recommend_category_final = "Politics & Social Sciences"
	elif recommend_category == "Reference":
		recommend_category_final = "Reference"
	elif recommend_category == "Christian":
		recommend_category_final = "Christian Books & Bibles"	
	elif recommend_category == "Religion":
		recommend_category_final = "Religion & Spirituality"
	elif recommend_category == "Sports":
		recommend_category_final = "Sports & Outdoors"
	elif recommend_category == "Teen":
		recommend_category_final = "Teen & Young Adult"	
	elif recommend_category == "Children's Books":
		recommend_category_final = "Children's Books"	
	elif recommend_category == "Travel":
		recommend_category_final = "Travel"
	return recommend_category_final