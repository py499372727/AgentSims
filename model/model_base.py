from base import Base


class ModelBase(Base):
    def __init__(self, app, cmd):
        super().__init__(app, cmd)

        # Indicate that whether the data has been retrived from database.
        self.is_retrieved = False
        # Indicate that whether the data has been modified.
        self.is_modified = False

        # Cached table name.
        self.table_name = None
        # Cached model name.
        self.model_name = None

    # Save model - simply change the modified flag.
    def save(self):
        self.is_modified = True

    # Save cachaed data into the database immediately.
    def flush(self):
        pass

    # Get the table name.
    # The default is the class name removed right 'Model'.
    def get_table_name(self):
        if self.table_name is None:
            self.table_name = self.__class__.__name__.removesuffix('Model').lower()
        return self.table_name

    # Get the model name.
    # The default is the class name removed right 'Model'.
    def get_model_name(self):
        if self.model_name is None:
            self.model_name = self.__class__.__name__.removesuffix('Model')
        return self.model_name
