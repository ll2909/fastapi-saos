import vt

def load_vt_key():
  f = open("./vtapi_key",  "r")
  key = f.read()
  f.close()
  return key

async def upload_hashes(file_path):
  """Uploads selected file to VirusTotal."""

  async with vt.Client(load_vt_key()) as client:
    with open(file_path, 'rb') as f:    
        analysis = await client.scan_file_async(file=f)
        print(f"File {file_path} uploaded.")

  return analysis, file_path

async def process_analysis_results(analysis):
  async with vt.Client(load_vt_key()) as client:
    completed_analysis = await client.wait_for_analysis_completion(analysis)
    return completed_analysis.stats, completed_analysis.id


async def analyze_file_vt(filepath):
  # Upload the file and get an analysis object for it.
  analysis, file_path = await upload_hashes(filepath)
  print("File path: ", file_path)
  print("Analysis id: ", analysis)
  stats, id = await process_analysis_results(analysis)
  return stats, id