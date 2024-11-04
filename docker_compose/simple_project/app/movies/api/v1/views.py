from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.generic.list import BaseListView
from movies.models import FilmWork, Roles
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.paginator import Paginator
from django.views.generic.detail import BaseDetailView

from django.db.models import Q, F

def api(request):
    return HttpResponse("My best API")

class MoviesApiMixin:
    model = FilmWork
    http_method_names=['get']
    
    def get_queryset(self):
        movies = FilmWork.objects.annotate(
            genres_list=ArrayAgg('genres__name', distinct=True),
            # persons_list=ArrayAgg('persons__full_name', distinct=True),
            actors=ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=Roles.ACTOR), distinct=True),
            directors = ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=Roles.DIRECTOR),  distinct=True),
            writers = ArrayAgg('persons__full_name', filter=Q(personfilmwork__role=Roles.WRITER), distinct=True),
        )
        
        return movies
    
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context) 


class MoviesListApi(MoviesApiMixin, BaseListView):
    model = FilmWork
    http_method_names = ['get'] 
    paginate_by=50
    
    def paginate_queryset(self, queryset, page_size):
        paginator=Paginator(queryset, page_size)
        page_num=self.request.GET.get('page', 1)
        if page_num=='last':
            page_num=paginator.num_pages
        page=paginator.get_page(page_num)
        
        return (paginator, page, page.object_list, page.has_next())
    
    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = super().get_queryset().values("id","title", "description","creation_date","rating","type", 'genres_list', "actors", "directors", "writers")
        paginator, page, queryset, next = self.paginate_queryset(queryset, self.paginate_by)
        context = {
                'count': paginator.count,
                'total_pages':paginator.num_pages,
                'prev': page.previous_page_number() if page.has_previous() else None,
                'next': page.next_page_number() if next else None,
                'results': list(queryset),
                }
        
        for result in context['results']:
            result['genres']=result.pop('genres_list')
            if result['writers']==None:
                result['writers']=[""]
            if result['directors']==None:
                result['directors']=[""]
            if result['actors']==None:
                result['actors']=[""]
        return context

class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    
    def get_context_data(self, **kwargs):        
       
        queryset = self.get_queryset().filter(id=self.kwargs.get('pk'))
        context = queryset.values("id","title", "description","creation_date","rating","type", 'genres_list', "actors", "directors", "writers", ).first()
        
        context['genres']=context.pop('genres_list')
            
        return context
        
    
    
    
    
