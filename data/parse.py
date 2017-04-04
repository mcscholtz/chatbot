import bigbang
import chakoteya
import movie
import stats
import reddit

#bigbang.parse('bigbang')
#stats.parse('bigbang.conv', 'bigbang')

#movie.parse('movie')
#stats.parse('movie.conv', 'movie')

#chakoteya.parse('chakoteya')
#stats.parse('chakoteya.conv', 'chakoteya')

reddit.merge('reddit.conv','reddit')
stats.parse('reddit.conv', 'reddit')
