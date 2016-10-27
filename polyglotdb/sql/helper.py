from sqlalchemy.sql.expression import ClauseElement
from .models import (AnnotationType, PropertyType, Property,
                        NumericProperty, Annotation, Speaker, Discourse,
                        SpeakerProperty, DiscourseProperty, SpeakerAnnotation)
import time
import sys
def get_or_create(session, model, defaults=None, **kwargs):
    """
    either get or create a row in the sql table specified by model

    Parameters
    ----------
    Session : corpus_context.sqlsession 
        the current sql session
    model : a  ~declarative_base model
        the table to add data to
    defaults:

    **kwargs: 
        the data to add
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


def get_or_create_all(session, tup):
    """
    takes a tuple of num_props and props lists
    """

    # tup = (nums, props)
    # nums = {id: [(ann2, prop1, value1), (ann2, prop2, value2)]}

    


    print('in get or create all')
    toret = []

    n_labels = list(tup[0].keys())
    p_labels = list(tup[1].keys())
    
    # limit is 999, so chunk the list
    while(len(n_labels) > 0):
        toadd = []
        for i in range(min(999,len(n_labels))):
            toadd.append(n_labels[i])   
            n_labels.remove(n_labels[i])

        print(toadd)

        num_instance = session.query(NumericProperty).filter(Annotation.id.in_(toadd))
        
        instances = num_instance.all()

        
        print(instances)
        exclude = [x.id for x in instances]
        exclude = set(exclude)
        
        # found_nums = [x.annotation_id for x in num_instance]
        # print(found_nums)
        # exclude = set(found_nums)
        for k,v in tup[0].items():
            if k in exclude:
                sys.exit()
            for p in v:
                params = {'annotation': p[0], 'property_type' : p[1], 'value' : p[2]}
                instance = model(**params)
                session.add(instance)
                print("added {}".format(params))
                sys.exit()
                # return instance, True

        break
    # for all of the instances not found
    #   params = 


   ## print(num_instance.all())
    
    p_instance = session.query(Property).filter(Annotation.id.in_(p_annotation_list))
    if num_instance or p_instance:
        print(num_instance)
        print(p_instance)
        print("was found somewhere")
        return num_instance, p_instance, False
    else:
        pass