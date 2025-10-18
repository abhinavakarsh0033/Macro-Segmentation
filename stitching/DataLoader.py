import os, zipfile
from torch.utils.data import Dataset
from datasets import load_dataset
from huggingface_hub import list_repo_files, hf_hub_download

class CustomDataset(Dataset):
    def __init__(self, image_dir, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        dataset_name = "FanqingM/MMIU-Benchmark"
        self.dataset = load_dataset(dataset_name, split="test")

        # Download and extract zip files from the dataset repository
        # repo_files = list_repo_files(dataset_name, repo_type="dataset")
        # zip_files = [f for f in repo_files if f.endswith('.zip')]
        # print(zip_files)
        # for z in zip_files:
        #     z1 = hf_hub_download(repo_id=dataset_name, filename=z, repo_type="dataset")
        #     extract_dir = z.replace('.zip', '')
        #     extract_dir = os.path.join(self.image_dir, extract_dir)
        #     if not os.path.exists(extract_dir): # Avoid re-extracting
        #         os.makedirs(extract_dir)
        #         with zipfile.ZipFile(z1, 'r') as zip_ref:
        #             zip_ref.extractall(extract_dir)
        #     else:
        #         print(f"Directory {extract_dir} already exists, skipping extraction. If it doesn't contain the required data, please delete this directory and rerun.")

        self.idx = 0

        # For now flattening as a list of images... Will decide later if want to keep them grouped
        self.__image_paths = []
        for item in self.dataset:
            for path in item["input_image_path"]:
                # Remove leading "./" if present
                clean_path = path.lstrip("./")
                abs_path = os.path.join(self.image_dir, clean_path)
                self.__image_paths.append(abs_path)
        print(f"Dataset initialized with {len(self.__image_paths)} images.")

    def __len__(self):
        return len(self.__image_paths)

    def __getitem__(self, idx):
        return self.__image_paths[idx]
    
    def get_next_image(self):
        if self.idx >= len(self.__image_paths):
            raise IndexError("No more images in the dataset.")
        image_path = self.__image_paths[self.idx]
        self.idx += 1
        return image_path
    
    def get_images(self, count):
        if self.idx + count > len(self.__image_paths):
            raise IndexError("Not enough images left in the dataset.")
        image_paths = self.__image_paths[self.idx:self.idx + count]
        self.idx += count
        return image_paths