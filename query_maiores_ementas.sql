select '|' || nome_ementa || '|', count(*) from acordao_ementa ae
group by 1
order by 2 desc
