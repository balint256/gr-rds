/* -*- c++ -*- */
/*
 * This block creates the baseband (NRZ, i.e. [-1, 1]) RDS signal.
 * 
 * It reads its configuration from an XML file, takes as input a stream 
 * at the desired sampling rate carrying a signal of 1187.5 Hz (19kHz/16, use
 * the rds.freq_divider block to create it), and outputs a bitstream of RDS
 * data at 1187.5bps at the same sampling rate.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gr_rds_data_encoder.h>
#include <gr_io_signature.h>
#include <math.h>

gr_rds_data_encoder_sptr gr_rds_make_data_encoder (const char *xmlfile) {
	return gr_rds_data_encoder_sptr (new gr_rds_data_encoder (xmlfile));
}

gr_rds_data_encoder::gr_rds_data_encoder (const char *xmlfile)
  : gr_sync_block ("gr_rds_data_encoder",
			gr_make_io_signature (1, 1, sizeof(float)),
			gr_make_io_signature (1, 1, sizeof(float)))
{
// initializes the library, checks for potential ABI mismatches
	LIBXML_TEST_VERSION
	reset_rds_data();
	read_xml(xmlfile);
	create_groups(0, false);
	prepare_buffers();
}

gr_rds_data_encoder::~gr_rds_data_encoder () {
	xmlCleanupParser();		// Cleanup function for the XML library
	xmlMemoryDump();		// this is to debug memory for regression tests
}

void gr_rds_data_encoder::reset_rds_data(){
	int i=0;
	for(i=0; i<4; i++) {infoword[i]=0; checkword[i]=0;}
	for(i=0; i<104; i++) {buffer[i]=0; diff_enc_buffer[i]=0;}
	d_buffer_bit_counter=0;
	d_buffer_current=0;
	d_sign_last=0;
	d_zero_cross=0;
	d_current_out=0;
	d_g0_counter=0;

	PI=0;
	TP=false;
	PTY=0;
	TA=false;
	MuSp=false;
	MS=false;
	AH=false;
	compressed=false;
	static_pty=false;
	memset(PS,' ',sizeof(PS));
	memset(radiotext,' ',sizeof(radiotext));
	radiotext_AB_flag=0;
}


////////////////////  READING XML FILE  //////////////////

/* assinging the values from the xml file to our variables
 * i could do some more checking for invalid inputs,
 * but leaving as is for now */
void gr_rds_data_encoder::assign_from_xml
(const char *field, const char *value, const int length){
	if(!strcmp(field, "PI")){
		if(length!=4) printf("invalid PI string length: %i\n", length);
		else PI=strtol(value, NULL, 16);
	}
	else if(!strcmp(field, "TP")){
		if(!strcmp(value, "true")) TP=true;
		else if(!strcmp(value, "false")) TP=false;
		else printf("unrecognized TP value: %s\n", value);
	}
	else if(!strcmp(field, "PTY")){
		if((length!=1)&&(length!=2))
			printf("invalid TPY string length: %i\n", length);
		else PTY=atol(value);
	}
	else if(!strcmp(field, "TA")){
		if(!strcmp(value, "true")) TA=true;
		else if(!strcmp(value, "false")) TA=false;
		else printf("unrecognized TA value: %s\n", value);
	}
	else if(!strcmp(field, "MuSp")){
		if(!strcmp(value, "true")) MuSp=true;
		else if(!strcmp(value, "false")) MuSp=false;
		else printf("unrecognized MuSp value: %s\n", value);
	}
	else if(!strcmp(field, "AF1")) AF1=atof(value);
	else if(!strcmp(field, "AF2")) AF2=atof(value);
/* need to copy a char arrays here */
	else if(!strcmp(field, "PS")){
		if(length!=8) printf("invalid PS string length: %i\n", length);
		else for(int i=0; i<8; i++)
			PS[i]=value[i];
	}
	else if(!strcmp(field, "RadioText")){
		if(length>64) printf("invalid RadioText string length: %i\n", length);
		else for(int i=0; i<length; i++)
			radiotext[i]=value[i];
	}
	else printf("unrecognized field type: %s\n", field);
}

/* recursively print the xml nodes */
void gr_rds_data_encoder::print_element_names(xmlNode * a_node){
	xmlNode *cur_node = NULL;
	char *node_name='\0', *attribute='\0', *value='\0';
	int length=0;

	for (cur_node = a_node; cur_node; cur_node = cur_node->next) {
		if (cur_node->type == XML_ELEMENT_NODE){
			node_name=(char*)cur_node->name;
			if(!strcmp(node_name, "rds")) ;		//move on
			else if(!strcmp(node_name, "group")){
				attribute=(char*)xmlGetProp(cur_node, (const xmlChar *)"type");
				printf("\ngroup type: %s  ###  ", attribute);
			}
			else if(!strcmp(node_name, "field")){
				attribute=(char*)xmlGetProp(cur_node, (const xmlChar *)"name");
				value=(char*)xmlNodeGetContent(cur_node);
				length=xmlUTF8Strlen(xmlNodeGetContent(cur_node));
				printf("%s: %s # ", attribute, value);
				assign_from_xml(attribute, value, length);
			}
			else printf("invalid node name: %s\n", node_name);
		}
		print_element_names(cur_node->children);
	}
}

/* open the xml file, confirm that the root element is "rds",
 * then recursively print it and assign values to the variables.
 * for now, this runs once at startup. in the future, i might want
 * to read periodically (say, each 5 sec?) so as to change values
 * in the xml file and see the results in the "air"... */
int gr_rds_data_encoder::read_xml (const char *xmlfile){
	xmlDoc *doc;
	xmlNode *root_element = NULL;

	doc = xmlParseFile(xmlfile);
	if (doc == NULL) {
		fprintf(stderr, "Failed to parse %s\n", xmlfile);
		return 1;
	}
	root_element = xmlDocGetRootElement(doc);
// The root element MUST be "rds"
	if(strcmp((char*)root_element->name, "rds")){
		fprintf(stderr, "invalid XML root element!\n");
		return 1;
	}
	print_element_names(root_element);
	printf("\n");

	xmlFreeDoc(doc);
	return 0;
}



//////////////////////  CREATE DATA GROUPS  ///////////////////////

/* see Annex B, page 64 of the standard */
unsigned int gr_rds_data_encoder::calc_syndrome(unsigned long message, 
			unsigned char mlen, unsigned long poly, unsigned char plen) {
	unsigned long reg=0;
	unsigned int i;

	for (i=mlen;i>0;i--)  {
		reg=(reg<<1) | ((message>>(i-1)) & 0x01);
		if (reg & (1<<plen)) reg=reg^poly;
	}
	for (i=plen;i>0;i--) {
		reg=reg<<1;
		if (reg & (1<<plen)) reg=reg^poly;
	}
	return (reg & ((1<<plen)-1));
}

/* see page 41 in the standard; this is an implementation of AF method A
 * FIXME need to add code that declares the number of AF to follow... */
unsigned int gr_rds_data_encoder::encode_af(const double af){
	unsigned int af_code=0;
	if((af>=87.6)&&(af<=107.9))
		af_code=nearbyint((af-87.5)*10);
	else if((af>=153)&&(af<=279))
		af_code=nearbyint((af-144)/9);
	else if((af>=531)&&(af<=1602))
		af_code=nearbyint((af-531)/9+16);
	else
		printf("invalid alternate frequency: %f\n", af);
	return(af_code);
}

/* create the 4 infowords, according to group type.
 * then calculate checkwords and put everything in the groups */
void gr_rds_data_encoder::create_groups(const int group_type, const bool AB){
	int i=0;
	
	infoword[0]=PI;
	infoword[1]=(((char)group_type)<<12)|(AB<<11)|(TP<<10)|(PTY<<5);

// FIXME make this prepare also group types !=0
	if(group_type==0){
		infoword[1]=infoword[1]|(TA<<4)|(MuSp<<3);
		if(d_g0_counter==3)
			infoword[1]=infoword[1]|0x5;	// d0=1 (stereo), d1-3=0
		infoword[1]=infoword[1]|(d_g0_counter&0x3);
		if(!AB)
			infoword[2]=((encode_af(AF1)&0xff)<<8)|(encode_af(AF2)&0xff);
		else
			infoword[2]=PI;
		infoword[3]=(PS[2*d_g0_counter]<<8)|PS[2*d_g0_counter+1];
		d_g0_counter++;
		if (d_g0_counter>3) d_g0_counter=0;
	}
	printf("data: %04X %04X %04X %04X\n",
		infoword[0], infoword[1], infoword[2], infoword[3]);

	for(i=0;i<4;i++){
		checkword[i]=calc_syndrome(infoword[i],16,0x5b9,10);
		block[i]=((infoword[i]&0xffff)<<10)|(checkword[i]&0x3ff);
	}
	printf("group: %04X %04X %04X %04X\n",
		block[0], block[1], block[2], block[3]);
}

void gr_rds_data_encoder::prepare_buffers(){
	int q=0, i=0, j=0, a=0, b=0;
	unsigned char temp[13];	// 13*8=104
	for(i=0; i<13; i++) temp[i]=0;
	
	for (q=0;q<104;q++){
		a=floor(q/26); b=25-q%26;
		buffer[q]=(block[a]>>b)&0x1;
		i=floor(q/8); j=7-q%8;
		temp[i]=temp[i]|(buffer[q]<<j);
	}
	printf("buffer: ");
	for(i=0;i<13;i++) printf("%02X ", temp[i]);
	printf("\n");
	
	for(i=0; i<13; i++) temp[i]=0;
	diff_enc_buffer[0]=buffer[0];
	temp[0]=buffer[0]<<7;
	for (q=1;q<104;q++){
		diff_enc_buffer[q]=(buffer[q]==buffer[q-1])?0:1;
		i=floor(q/8); j=7-q%8;
		temp[i]=temp[i]|(diff_enc_buffer[q]<<j);
	}
	printf("diff-encoded buffer: ");
	for(i=0;i<13;i++) printf("%02X ", temp[i]);
	printf("\n");
}



//////////////////////// WORK ////////////////////////////////////

/* the plan for now is to do group0 (basic), group2 (radiotext),
 * group4a (clocktime), and group8a (tmc)... */
/* FIXME make this output >1 groups */
int gr_rds_data_encoder::work (int noutput_items,
					gr_vector_const_void_star &input_items,
					gr_vector_void_star &output_items)
{
	const float *in = (const float *) input_items[0];
	float *out = (float *) output_items[0];
	int sign_current=0;
	
	// initialize output buffer
	d_current_out=(diff_enc_buffer[d_buffer_bit_counter]?1:-1);

	for(int i=0; i<noutput_items; i++){
		sign_current=(in[i]>0?1:-1);
		if(sign_current!=d_sign_last){
			if(++d_zero_cross==2){		// double zero-cross; push next bit
				d_zero_cross=0;
				if(++d_buffer_bit_counter>103) d_buffer_bit_counter=0;
				d_current_out=(diff_enc_buffer[d_buffer_bit_counter]?1:-1);	// NRZ
			}
		}
		out[i]=d_current_out;
		d_sign_last=sign_current;
	}

	return noutput_items;
}
