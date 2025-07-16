class MessageHandler:
    def __init__(self, local_mode = False):
        self.local_mode = local_mode
        self.db_client = Supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"), local_mode)
        self.meta_io = MetaIO(os.getenv("META_IO_URL"), os.getenv("META_IO_KEY"), local_mode)
