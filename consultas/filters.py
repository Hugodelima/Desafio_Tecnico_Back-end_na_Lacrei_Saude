import django_filters
from django.utils import timezone
from .models import Consulta

class ConsultaFilter(django_filters.FilterSet):
    profissional = django_filters.NumberFilter(field_name='profissional__id')
    profissional_nome = django_filters.CharFilter(field_name='profissional__nome_social', lookup_expr='icontains')
    
    data = django_filters.DateFilter(field_name='data')
    data_min = django_filters.DateFilter(field_name='data', lookup_expr='gte')
    data_max = django_filters.DateFilter(field_name='data', lookup_expr='lte')
    
    horario_min = django_filters.TimeFilter(field_name='data__time', lookup_expr='gte')
    horario_max = django_filters.TimeFilter(field_name='data__time', lookup_expr='lte')
    
    periodo = django_filters.ChoiceFilter(
        choices=[
            ('hoje', 'Hoje'),
            ('amanha', 'Amanhã'),
            ('semana', 'Esta semana'),
            ('mes', 'Este mês'),
            ('futuro', 'Futuro'),
            ('passado', 'Passado')
        ],
        method='filter_periodo'
    )
    
    class Meta:
        model = Consulta
        fields = ['profissional', 'data', 'data_min', 'data_max']
    
    def filter_periodo(self, queryset, name, value):
        hoje = timezone.now().date()
        
        if value == 'hoje':
            return queryset.filter(data__date=hoje)
        elif value == 'amanha':
            return queryset.filter(data__date=hoje + timezone.timedelta(days=1))
        elif value == 'semana':
            start_week = hoje - timezone.timedelta(days=hoje.weekday())
            end_week = start_week + timezone.timedelta(days=6)
            return queryset.filter(data__date__range=[start_week, end_week])
        elif value == 'mes':
            return queryset.filter(data__month=hoje.month, data__year=hoje.year)
        elif value == 'futuro':
            return queryset.filter(data__gt=timezone.now())
        elif value == 'passado':
            return queryset.filter(data__lt=timezone.now())
        
        return queryset