from django.db import migrations

# Trigger PostgreSQL : maintient search_vector (config 'french') à partir de
# objet + correspondant + annotations_directeur + observation (CDC 2.2).
TRIGGER_SQL = """
CREATE FUNCTION courriers_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    to_tsvector('french',
      coalesce(NEW.objet, '') || ' ' ||
      coalesce(NEW.correspondant, '') || ' ' ||
      coalesce(NEW.annotations_directeur, '') || ' ' ||
      coalesce(NEW.observation, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER courriers_search_vector_trigger
  BEFORE INSERT OR UPDATE OF objet, correspondant, annotations_directeur, observation
  ON courriers_courrier
  FOR EACH ROW EXECUTE FUNCTION courriers_search_vector_update();

UPDATE courriers_courrier SET objet = objet;
"""

REVERSE_SQL = """
DROP TRIGGER IF EXISTS courriers_search_vector_trigger ON courriers_courrier;
DROP FUNCTION IF EXISTS courriers_search_vector_update();
"""


class Migration(migrations.Migration):

    dependencies = [
        ("courriers", "0002_courrier_search_vector_and_more"),
    ]

    operations = [
        migrations.RunSQL(TRIGGER_SQL, REVERSE_SQL),
    ]
