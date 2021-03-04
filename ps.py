import win32pdh
object = 'Process'
items, instances = win32pdh.EnumObjectItems(None, None, object,
                                            win32pdh.PERF_DETAIL_WIZARD)
instance_dict = {}
for instance in instances:
   try:
      instance_dict[instance] = instance_dict[instance] + 1
   except KeyError:
      instance_dict[instance] = 0
counters = {}
hcs = []
hq = win32pdh.OpenQuery()
for instance, max_instances in instance_dict.items():
   for inum in range(max_instances+1):
      if instance == 'chrome':
         path = win32pdh.MakeCounterPath((None,object,instance,
                                          None,inum,'Creating Process ID'))
         hcs.append(win32pdh.AddCounter(hq,path))
win32pdh.CollectQueryData(hq)
for hc in hcs:
   try:
      type,val=win32pdh.GetFormattedCounterValue(hc,win32pdh.PDH_FMT_LONG)
   except win32pdh.counter_status_error:
      pass
   try:
      counters[val] += 1
   except KeyError:
      counters[val] = 1
   win32pdh.RemoveCounter(hc)
win32pdh.CloseQuery(hq)
