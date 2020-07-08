class CustCR(pykorm.CustomObject('ch.pykorm', 'v1', 'custCR')):
    the_spec = pykorm.fields.Spec('.the_spec')
    the_annotation = pykorm.fields.Metadata('.annotations.the_annotation')


    def __init__(self, name, the_spec):
        self.name = name
        self.the_spec = the_spec



pk = pykorm()

ccr1 = CustCR('ccr1', 'ts1')
pk.save(ccr1)