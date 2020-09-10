import pandas as pd
import numpy as np
import re
from collections import Counter


movies_col =['movie_id','movie_name','genre']
movies = pd.read_table('/Users/darrenlee/PycharmProjects/overture/data/pfda/ml-1m/movies.dat',sep = '::',header= None,names = movies_col, engine = 'python')

ratings_col =['user_id','movie_id','rating','timestamp']
ratings = pd.read_table('/Users/darrenlee/PycharmProjects/overture/data/pfda/ml-1m/ratings.dat',sep = '::',header= None,names = ratings_col, engine = 'python')

users_col = ['user_id','gender','age','occupation','zip_code']
users = pd.read_table('/Users/darrenlee/PycharmProjects/overture/data/pfda/ml-1m/users.dat',sep = '::',header= None,names= users_col, engine = 'python')

mv_rt = pd.merge(movies, ratings, on = "movie_id", how = "left")

mv_rating = pd.merge(mv_rt, users, on = "user_id", how = 'left' )


occupation_dict = {0: "other"
,1: "academic/educator"
,2: "artist"
,3: "clerical/admin"
,4: "college/grad student"
,5: "customer service"
,6: "doctor/health care"
,7: "executive/managerial"
,8: "farmer"
,9: "homemaker"
,10: "K-12 student"
,11: "lawyer"
,12: "programmer"
,13: "retired"
,14: "sales/marketing"
,15: "scientist"
,16: "self-employed"
,17: "technician/engineer"
,18: "tradesman/craftsman"
,19: "unemployed"
,20: "writer"}

# occupation title merge
occupation_df = pd.DataFrame.from_dict(occupation_dict,orient='index', columns =["occupation_title"]).reset_index()
mv_rating = pd.merge(mv_rating, occupation_df, left_on = 'occupation' , right_on = 'index', how = 'left')


bins = [0,18,24,34,44,55,100]
labels = ['Under 18', '18-24', '25-34', '35-44', '45-55','56+']

mv_rating['age_range'] = pd.cut(x=mv_rating['age'], bins=bins,
                    labels= labels, include_lowest= True)

mv_rating[['age','age_range']]


#4 mv_rating의 영화 제목 컬럼에서 개봉 연도를 분리해서 추가 컬럼을 생성해 주세요.
# mv_rating["year"]

def split_it(year):
    return re.findall('\(.*?\)', year)


mv_rating["year"] = mv_rating.movie_name.apply(lambda x : re.findall('(?<=\()\d+', x)[0])

mv_rating

#5 전체 영화의 개수와 평균 평점, 평점 개수를 구해 출력해 주세요.

# 전체 영화 갯수
total_movie_num = mv_rating.movie_name.nunique()

#5
# 평균 평점
avg_rating = mv_rating.rating.mean()

# 평균 평점 갯수
avg_rating_by_mv = mv_rating["movie_name"].value_counts().mean()

print(f"총 영화 갯수 :{total_movie_num} \n 평균 평점 :{avg_rating:.2f} \n 영화 별 평균 평점 갯수: {avg_rating_by_mv:.2f}")


#6 영화별 평균 평점/ 평점 갯수 구하고 dataframe칼럼으로 추가
movies_info = pd.DataFrame()

func_list = ["size","mean"]

movies_info = mv_rating[["movie_name","rating"]].groupby(mv_rating["movie_name"]).agg(func_list)
movies_info.columns = movies_info.columns.droplevel(0)
movies_info.reset_index(inplace= True)

movies_info = movies_info.rename(columns = {'' : "movieName","size": "numberOfReviews", "mean":"averageRating"})

# 평균 평점이 가장 높은 영화 TOP10과 가장 낮은 WORST10을 구해 출력해 주세요.
movies_info.sort_values(by = ["averageRating","numberOfReviews"], ascending = False).head(10)
movies_info.sort_values(by = ["averageRating","numberOfReviews"], ascending = True).head(10)

# User 당 평균 평점 개수를 구해 출력해 주시고, 평점을 가장 많이 남긴 User TOP10을 출력해 주세요.
mv_rating.columns
# 평균 평점 갯수
mv_rating.groupby(mv_rating["user_id"]).agg("size").mean()
# top 10 number of reviews
mv_rating.groupby(mv_rating["user_id"]).agg("size").sort_values(ascending=False).head(10)

# mv_rating의 장르 컬럼에 들어갈 수 있는 장르를 별도의 데이터 프레임으로 생성해주세요.데이터 프레임 이름은 mv_genre_list로 지정해 주세요.
mv_genre_list = list(mv_rating["genre"].str.split("|", expand =True).unstack().unique())



#10. mv_genre_list를 활용하여 각 장르에 포함되는 영화의 개수와 평균 평점, 장르별 평점 개수를 구해 출력해 주세요.
mv_genre_df = pd.DataFrame(mv_genre_list, columns= ["genre"])

# movies_info_genre = pd.merge(movies_info ,mv_rating[["movie_name","genre"]], on = "movie_name" , how = "left")
movies_info = pd.merge(movies_info, movies, on = "movie_name", how = "inner")

# 장르별 영화 갯수
movieNumByGenre = movies_info["genre"].str.split("|", expand = True).unstack().value_counts()

# 장르 별 평균 평점
genre_unstack = mv_rating["genre"].str.split("|", expand = True)
tmp_df = genre_unstack.rename(columns = {0:"genre1",1:"genre2",2:"genre3",3:"genre4",4:"genre5",5:"genre6"})
tmp_df.columns

mv_rating2 = pd.concat([mv_rating, tmp_df], axis = 1)
# melt

melted_rating2 = mv_rating2.melt(id_vars =['movie_id', 'movie_name', 'genre', 'user_id', 'rating', 'timestamp',
       'gender', 'age', 'occupation', 'zip_code', 'index', 'occupation_title',
       'age_range', 'year'], value_vars = ['genre1', 'genre2', 'genre3', 'genre4', 'genre5',
       'genre6'] , var_name = ["genre"])


# drop rows with None (genre columns)
melted_rating2 = melted_rating2.dropna(subset = ['value'],axis = 0)

# value counts
mv_rating[["movie_name","rating"]].groupby(mv_rating["movie_name"]).agg(func_list)

rating_by_genre = melted_rating2[["movie_name","rating"]].groupby(melted_rating2["value"]).agg(func_list)
rating_by_genre = rating_by_genre.reset_index()
rating_by_genre


# 장르 별 평점 갯수
mv_rating_df = mv_rating["genre"].str.split("|", expand = True).unstack().value_counts()


