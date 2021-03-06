from django.db import IntegrityError, transaction
from curation.parsers.generic import GenericData
from curation.parsers.trait import TraitData
from catalog.models import Score


class ScoreData(GenericData):

    def __init__(self,score_name):
        GenericData.__init__(self)
        self.name = score_name
        self.data = {'name': score_name}


    @transaction.atomic
    def create_score_model(self,publication):
        '''
        Create an instance of the Score model.
        It also create instance(s) of the EFOTrait model if needed.
        - publication: instance of the Publication model
        Return type: Score model
        '''
        try:
            with transaction.atomic():
                self.model = Score()
                self.model.set_score_ids(self.next_id_number(Score))
                for field, val in self.data.items():
                    if field == 'trait_efo':
                        efo_traits = []
                        for trait_id in val:
                            trait_id = trait_id.replace(':','_').strip()
                            trait = TraitData(trait_id)
                            efo = trait.efotrait_model()
                            efo_traits.append(efo)
                    else:
                        setattr(self.model, field, val)
                # Associate a Publication
                self.model.publication = publication
                self.model.save()

                for efo in efo_traits:
                    self.model.trait_efo.add(efo)
                self.model.save()
        except IntegrityError as e:
            self.model = None
            print('Error with the creation of the Score(s) and/or the Trait(s)')
        return self.model