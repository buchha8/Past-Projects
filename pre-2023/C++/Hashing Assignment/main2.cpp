#include <cstdlib>
#include <math.h>
#include <vector>
#include <algorithm>
#include "image.h"

// ===================================================================================================
// ===================================================================================================

//sorts the vector by the size of the vectors in each element
bool sorter_helper(const std::vector<std::pair<int, int> >  a, const std::vector<std::pair<int, int> >  b)
{
  return a.size() > b.size();
}


/*EXAMPLE, where the number in the matrix corresponds to the size of the vector

-------
|6|4|9|
|3|2|8|
|1|5|7|
-------

becomes 

|1|3|6|5|2|4|7|8|9|
which sorts to
|9|8|7|6|5|4|3|2|1|

when the bottomleft corner is (0,0)

*/



void Compress(const Image<Color> &input, 
              Image<bool> &occupancy, Image<Color> &hash_data, Image<Offset> &offset) {

  
  occupancy.Allocate(input.Width(), input.Height());

  //number of non-white pixels
  int p = 0;

  //this nested for-loop counts number of non-white pixels and creates occupancy image
  for(int i = 0; i < input.Width(); i++)
  {
    for(int j = 0; j < input.Height(); j++)
    {
      if(!((input.GetPixel(i,j)).isWhite()))
      {
        p++;
        occupancy.SetPixel(i,j, true);
      }
      else
        occupancy.SetPixel(i,j, false);
    }
  }

  //provided formulas
  int s_hash = ceil(sqrt(1.01*p));
  int s_offset = ceil(sqrt(p/4.0));

  hash_data.Allocate(s_hash, s_hash);
  offset.Allocate(s_offset, s_offset);

  //sorted_coordinates is what I use to help keep track of information
  //the pair contains the i,j coordinates from a pixel the original image
  //if a vector has multiple pairs, that means that they are colliding
  std::vector<std::vector< std::pair<int, int> > > sorted_coordinates;
  sorted_coordinates.resize(s_offset*s_offset);

  for(int i = 0; i < input.Width(); i++)
  {
    for(int j = 0; j < input.Height(); j++)
    {
      if(!input.GetPixel(i,j).isWhite())
      {
        //make the 2D offset into a 1D vector of vectors of pairs for simplicity
        sorted_coordinates[(i%s_offset)*s_offset+(j%s_offset)].push_back(std::make_pair(i,j));
      }
    }
  }

  //when sorted, the offset with the most collisions will appear first
  std::sort(sorted_coordinates.begin(), sorted_coordinates.end(), sorter_helper);

  //if all collisions in a vector of pairs can be resolved with the same offset
  bool added = false;

  //if collisions cannot be resolved
  bool add_fail = false;

  for(int i = 0; i < sorted_coordinates.size(); i++)
  {
    unsigned char dx = 0;
    unsigned char dy = 0;
    added = false;
    add_fail = false;

    //keep looping through a set of colliding pixels until a solution is found or no offset works
    while(!added || add_fail)
    {
      //num_compatiable is the number of pixels that can be added with a given offset
      int num_compatible = 0;
      
      //each [i][j] is a different pixel
      for(int j = 0; j < sorted_coordinates[i].size(); j++)
      {
        //if a pixel can fit into the hash_data
        if(hash_data.GetPixel(((sorted_coordinates[i][j].first)%s_hash+dx)%s_hash,((sorted_coordinates[i][j].second)%s_hash+dy)%s_hash).isWhite())
        {
          num_compatible++; 
        }
        
      }
      //if all pixels can be added with a given offset
      if(num_compatible == sorted_coordinates[i].size())
      {
        //edit offset value and edit hash_data for each of the pixels
        for(int j = 0; j < sorted_coordinates[i].size(); j++)
        {
          offset.SetPixel((sorted_coordinates[i][j].first)%s_offset, (sorted_coordinates[i][j].second)%s_offset, Offset(dx, dy));
          hash_data.SetPixel(((sorted_coordinates[i][j].first)%s_hash+dx)%s_hash,((sorted_coordinates[i][j].second)%s_hash+dy)%s_hash, 
              input.GetPixel(sorted_coordinates[i][j].first,sorted_coordinates[i][j].second));

        }
        num_compatible=0;
        added = true;
      }

      //if pixels cannot be added, adjust dx and dy until no combinations will work
      else
      {
        dx++;
        if(dx>=s_hash)
        {
          dx=0;
          dy++;
        }
        if(dy>=s_hash)
        {
          add_fail = true;
        }
      }

    }
    //if pixel cannot be added, allocate more space and try again
    if(add_fail)
    {
      hash_data.Allocate(hash_data.Width()+1, hash_data.Height()+1);
      i--;
    }

  }


}


void UnCompress(const Image<bool> &occupancy, const Image<Color> &hash_data, const Image<Offset> &offset, 
                Image<Color> &output) {


  output.Allocate(occupancy.Width(), occupancy.Height());
  for(int i = 0; i < occupancy.Width(); i++)
  {

    for(int j = 0; j < occupancy.Height(); j++)
    {
      unsigned char dx = offset.GetPixel(i % offset.Width(),j%offset.Height()).dx;
      unsigned char dy = offset.GetPixel(i % offset.Width(),j%offset.Height()).dy;

      //if pixel is black, create pixel in output file with color pulled from hash_data
      if(occupancy.GetPixel(i,j))
        output.SetPixel(i, j, hash_data.GetPixel((i+dx)%hash_data.Width(), (j+dy)%hash_data.Height()));

    }
  }
}


// ===================================================================================================
// ===================================================================================================

// Takes in two 24-bit color images as input and creates a b&w output
// image (black where images are the same, white where different)
void Compare(const Image<Color> &input1, const Image<Color> &input2, Image<bool> &output) {

  // confirm that the files are the same size
  if (input1.Width() != input2.Width() ||
      input1.Height() != input2.Height()) {
    std::cerr << "Error: can't compare images of different dimensions: " 
         << input1.Width() << "x" << input1.Height() << " vs " 
         << input2.Width() << "x" << input2.Height() << std::endl;
  } else {
    // make sure that the output images is the right size to store the
    // pixel by pixel differences
    output.Allocate(input1.Width(),input1.Height());
    int count = 0;
    for (int i = 0; i < input1.Width(); i++) {
      for (int j = 0; j < input1.Height(); j++) {
        Color c1 = input1.GetPixel(i,j);
        Color c2 = input2.GetPixel(i,j);
        if (c1.r == c2.r && c1.g == c2.g && c1.b == c2.b)
          output.SetPixel(i,j,true);
        else {
          count++;
          output.SetPixel(i,j,false);
        }
      }      
    }     

    // confirm that the files are the same size
    if (count == 0) {
      std::cout << "The images are identical." << std::endl;
    } else {
      std::cout << "The images differ at " << count << " pixel(s)." << std::endl;
    }
  }
}

// ===================================================================================================
// ===================================================================================================

// to allow visualization of the custom offset image format
void ConvertOffsetToColor(const Image<Offset> &input, Image<Color> &output) {
  // prepare the output image to be the same size as the input image
  output.Allocate(input.Width(),input.Height());
  for (int i = 0; i < output.Width(); i++) {
    for (int j = 0; j < output.Height(); j++) {
      // grab the offset value for this pixel in the image
      Offset off = input.GetPixel(i,j);
      // set the pixel in the output image
      int dx = off.dx;
      int dy = off.dy;
      assert (dx >= 0 && dx <= 15);
      assert (dy >= 0 && dy <= 15);
      // to make a pretty image with purple, cyan, blue, & white pixels:
      int red = dx * 16;
      int green = dy *= 16;
      int blue = 255;
      assert (red >= 0 && red <= 255);
      assert (green >= 0 && green <= 255);
      output.SetPixel(i,j,Color(red,green,blue));
    }
  }
}

// ===================================================================================================
// ===================================================================================================

void usage(char* executable) {
  std::cerr << "Usage:  4 options" << std::endl;
  std::cerr << "  1)  " << executable << " compress input.ppm occupancy.pbm data.ppm offset.offset" << std::endl;
  std::cerr << "  2)  " << executable << " uncompress occupancy.pbm data.ppm offset.offset output.ppm" << std::endl;
  std::cerr << "  3)  " << executable << " compare input1.ppm input2.ppm output.pbm" << std::endl;
  std::cerr << "  4)  " << executable << " visualize_offset input.offset output.ppm" << std::endl;
}

// ===================================================================================================
// ===================================================================================================

int main(int argc, char* argv[]) {
  if (argc < 2) { usage(argv[1]); exit(1); }

  if (argv[1] == std::string("compress")) {
    if (argc != 6) { usage(argv[1]); exit(1); }
    // the original image:
    Image<Color> input;
    // 3 files form the compressed representation:
    Image<bool> occupancy;
    Image<Color> hash_data;
    Image<Offset> offset;
    input.Load(argv[2]);
    Compress(input,occupancy,hash_data,offset);
    // save the compressed representation
    occupancy.Save(argv[3]);
    hash_data.Save(argv[4]);
    offset.Save(argv[5]);

  } else if (argv[1] == std::string("uncompress")) {
    if (argc != 6) { usage(argv[1]); exit(1); }
    // the compressed representation:
    Image<bool> occupancy;
    Image<Color> hash_data;
    Image<Offset> offset;
    occupancy.Load(argv[2]);
    hash_data.Load(argv[3]);
    offset.Load(argv[4]);
    // the reconstructed image
    Image<Color> output;
    UnCompress(occupancy,hash_data,offset,output);
    // save the reconstruction
    output.Save(argv[5]);
  
  } else if (argv[1] == std::string("compare")) {
    if (argc != 5) { usage(argv[1]); exit(1); }
    // the original images
    Image<Color> input1;
    Image<Color> input2;    
    input1.Load(argv[2]);
    input2.Load(argv[3]);
    // the difference image
    Image<bool> output;
    Compare(input1,input2,output);
    // save the difference
    output.Save(argv[4]);

  } else if (argv[1] == std::string("visualize_offset")) {
    if (argc != 4) { usage(argv[1]); exit(1); }
    // the 8-bit offset image (custom format)
    Image<Offset> input;
    input.Load(argv[2]);
    // a 24-bit color version of the image
    Image<Color> output;
    ConvertOffsetToColor(input,output);
    output.Save(argv[3]);

  } else {
    usage(argv[0]);
    exit(1);
  }
}

// ===================================================================================================
// ===================================================================================================
