import mido

msg = mido.Message('note_on', note=60)
out = mido.open_output('Traktor Virtual Input')

out.send(msg)